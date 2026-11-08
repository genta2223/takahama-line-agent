import logging
from typing import Optional
from app.config import settings
from app.bot.prompt_template import get_system_prompt

logger = logging.getLogger(__name__)

# Fallback responses for offline or error conditions
FALLBACK_RESPONSES = {
    "policy": (
        "ご関心をお寄せいただきありがとうございます！阪口源太です。\n\n"
        "私は「80%の安心・継続 × 20%の独自性」のハイブリッド型政治を提唱しています。\n"
        "①現町政の良質な施策（子育て無償化・地域医療）を100%肯定・維持\n"
        "②約100億円の基金をハコモノ追認から守り抜く\n"
        "③青郷の国道27号青葉改良・南山手線延伸\n"
        "④東大松尾研等の知見を活かした優しい行政AX・迷わないLINE窓口\n\n"
        "詳細はリッチメニュー「阪口源太の重点政策10選」をご覧ください！"
    ),
    "default": (
        "温かいメッセージをありがとうございます！青郷出身の阪口源太です。\n\n"
        "高浜町の未来や地域の困りごとについて、町民の皆様の声を直接伺いながら政策に反映させてまいります。\n\n"
        "具体的な地域の道路・水路・安全対策のご要望は、リッチメニューの「地域の困りごと投稿フォーム」からも承っております。私自身が現場に足を運び、しっかりと確認いたします！"
    )
}

class GeminiService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.GEMINI_MODEL or "gemini-2.5-flash"
        self._model = None
        self._init_client()

    def _init_client(self):
        if not self.api_key:
            logger.warning("GEMINI_API_KEY is not set. Gemini service will use fallback mock responses.")
            return
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self._model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=get_system_prompt()
            )
            logger.info("Gemini client initialized with model: %s", self.model_name)
        except Exception as e:
            logger.error("Failed to initialize Gemini client: %s", e)
            self._model = None

    async def generate_response(self, user_message: str, user_id: Optional[str] = None) -> str:
        """Generate response from Gemini API as Genta Sakaguchi, with fallback handling."""
        if not self._model:
            # Check keywords for fallback
            text = user_message.lower()
            if any(k in text for k in ["政策", "マニフェスト", "公約", "10選", "考え"]):
                return FALLBACK_RESPONSES["policy"]
            return FALLBACK_RESPONSES["default"]

        try:
            # Use generate_content
            response = await self._model.generate_content_async(
                contents=user_message,
                generation_config={
                    "temperature": 0.4,
                    "max_output_tokens": 800,
                }
            )
            if response and response.text:
                return response.text.strip()
            return FALLBACK_RESPONSES["default"]
        except Exception as e:
            logger.error("Error generating Gemini response: %s", e)
            return (
                "メッセージをいただきありがとうございます。阪口源太です。\n\n"
                "ただいま通信環境によりAI応答が一時的に繋がりにくくなっております。"
                "いただいた内容は記録しておりますので、私自身が確認し、活動の参考にさせていただきます。\n"
                "地域の現場に関する緊急のご相談は「地域の困りごと投稿フォーム」もご利用ください。"
            )

gemini_service = GeminiService()

