import logging
import os

from app.schemas.generate import Attachment
from app.services.glm4v_service import GLM4VService

logger = logging.getLogger(__name__)

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}


async def process_attachments(
    body,
    glm4v_service: GLM4VService,
    *,
    on_image_progress=None,
) -> str:
    final_prompt = ""
    if body.prompt:
        final_prompt = f"用户需求：\n{body.prompt}"

    image_attachments = []
    text_attachments = []
    if body.attachments:
        image_attachments = [a for a in body.attachments if a.type == "image"]
        text_attachments = [a for a in body.attachments if a.type in ("text", "markdown")]

    if image_attachments:
        image_descriptions = []
        for idx, attachment in enumerate(image_attachments):
            logger.info(f"分析图片 {idx + 1}/{len(image_attachments)}: {attachment.name}")
            if on_image_progress:
                on_image_progress(idx, len(image_attachments), attachment)

            image_url = attachment.url
            is_base64 = False
            if image_url.startswith("/uploads/"):
                local_path = image_url[1:]
                if os.path.exists(local_path):
                    with open(local_path, "rb") as f:
                        image_url = GLM4VService.bytes_to_base64(f.read())
                        is_base64 = True
                    logger.info(f"图片已转换为Base64: {attachment.name}")

            try:
                image_result = await glm4v_service.describe_for_vue_generation(
                    image_source=image_url, is_base64=is_base64,
                )
                if image_result.get("success"):
                    image_descriptions.append(image_result["raw_description"])
                    logger.info(f"图片 {attachment.name} 分析完成，描述长度: {len(image_result['raw_description'])}")
                else:
                    logger.warning(f"图片 {attachment.name} 分析失败")
            except Exception as img_err:
                logger.error(f"图片 {attachment.name} 分析异常: {str(img_err)}")

        if not image_descriptions:
            logger.warning(f"所有图片分析均失败（共 {len(image_attachments)} 张）")

        if image_descriptions:
            combined = "\n\n".join([
                f"=== 图片 {i+1} 分析结果 ===\n{desc}"
                for i, desc in enumerate(image_descriptions)
            ])
            final_prompt = f"{final_prompt}\n\n图片分析结果：\n{combined}" if final_prompt else f"图片分析结果：\n{combined}"

    if text_attachments:
        text_contents = []
        for idx, attachment in enumerate(text_attachments):
            logger.info(f"读取文本 {idx + 1}/{len(text_attachments)}: {attachment.name}")
            file_url = attachment.url
            if file_url.startswith("/uploads/"):
                local_path = file_url[1:]
                if os.path.exists(local_path):
                    encodings = ["utf-8", "gbk", "gb2312", "latin-1"]
                    content = None
                    for enc in encodings:
                        try:
                            with open(local_path, "r", encoding=enc) as f:
                                content = f.read()
                            break
                        except (UnicodeDecodeError, LookupError):
                            continue
                    if content is not None:
                        label = "Markdown" if attachment.type == "markdown" else "文本"
                        text_contents.append(f"=== {label}文件 {idx + 1}: {attachment.name} ===\n{content}")
                        logger.info(f"文本文件 {attachment.name} 读取完成，内容长度: {len(content)}")
                    else:
                        logger.warning(f"文本文件 {attachment.name} 无法解码")
                else:
                    logger.warning(f"文本文件 {attachment.name} 本地路径不存在: {local_path}")

        if text_contents:
            combined = "\n\n".join(text_contents)
            final_prompt = f"{final_prompt}\n\n文本附件内容：\n{combined}" if final_prompt else f"文本附件内容：\n{combined}"

    if not final_prompt.strip():
        logger.warning("步骤0完成但final_prompt为空（无用户需求、无图片分析、无文本附件）")

    return final_prompt


def build_attachment_summary(attachments: list[Attachment] | None) -> str:
    if not attachments:
        return "已处理用户需求"
    image_count = len([a for a in attachments if a.type == "image"])
    text_count = len([a for a in attachments if a.type in ("text", "markdown")])
    parts = []
    if image_count > 0:
        parts.append(f"{image_count} 张图片")
    if text_count > 0:
        parts.append(f"{text_count} 个附件")
    return f"已处理{'、'.join(parts)}" if parts else "已处理用户需求"
