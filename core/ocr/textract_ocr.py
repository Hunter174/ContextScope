import boto3


class TextractOCR:
    def __init__(self, region="us-east-1"):
        self.client = boto3.client("textract", region_name=region)

    def extract(self, img_bytes: bytes) -> str:
        try:
            response = self.client.detect_document_text(
                Document={"Bytes": img_bytes}
            )

            lines = [
                block["Text"]
                for block in response.get("Blocks", [])
                if block["BlockType"] == "LINE"
            ]

            return "\n".join(lines)

        except Exception as e:
            print(f"Textract error: {e}")
            return ""