# handlers/text.py

from linebot.models import (
    MessageEvent,
    TextMessage,
    TextSendMessage,
)

def register_text_handler(handler, api, shopping_service):
    @handler.add(MessageEvent, message=TextMessage)
    def handle_text(event):
        text = event.message.text.strip()
        user_id = event.source.user_id

        # 群組 or 私聊 → 都用 source_id 當 conversation_id
        conversation_id = (
            event.source.group_id
            if hasattr(event.source, "group_id")
            else user_id
        )

        # --------------------
        # 1️⃣ 新增購物項目
        # --------------------
        if "要買" in text or "buy" in text.lower():
            items = shopping_service.add_items(
                conversation_id=conversation_id,
                user_id=user_id,
                text=text,
            )

            if not items:
                api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="⚠️ 沒有解析到任何購物項目")
                )
                return

            checklist = shopping_service.get_checklist(conversation_id)

            reply = ["✅ 已加入購物清單\n", "🛒 尚未購買："]
            for item in checklist["pending"]:
                reply.append(f"- {item['item_name']} ({item['created_by']})")

            api.reply_message(
                event.reply_token,
                TextSendMessage(text="\n".join(reply))
            )
            return

        # --------------------
        # 2️⃣ 查詢清單
        # --------------------
        if text == "清單":
            checklist = shopping_service.get_checklist(conversation_id)

            reply = ["🛒 尚未購買："]
            if checklist["pending"]:
                for item in checklist["pending"]:
                    reply.append(f"- {item['item_name']} ({item['created_by']})")
            else:
                reply.append("（沒有項目）")

            if checklist["today_completed"]:
                reply.append("\n✅ 今日已完成：")
                for item in checklist["today_completed"]:
                    reply.append(
                        f"- {item['item_name']}（完成者：{item['completed_by']}）"
                    )

            api.reply_message(
                event.reply_token,
                TextSendMessage(text="\n".join(reply))
            )
            return

        # --------------------
        # 3️⃣ 完成項目（文字）
        # --------------------
        if text.startswith("已買"):
            item_name = text.replace("已買", "").strip()

            shopping_service.complete_item(
                conversation_id=conversation_id,
                item_name=item_name,
                completed_by=user_id,
            )

            api.reply_message(
                event.reply_token,
                TextSendMessage(
                    text=f"✅ 已完成：{item_name}"
                )
            )
            return

        # --------------------
        # 4️⃣ 歷史
        # --------------------
        if text == "歷史":
            history = shopping_service.get_history(conversation_id)

            if not history:
                api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="📦 最近 7 天沒有購物紀錄")
                )
                return

            reply = ["📦 最近 7 天購物紀錄："]
            for item in history:
                reply.append(
                    f"- {item['item_name']}（完成者：{item['completed_by']}）"
                )

            api.reply_message(
                event.reply_token,
                TextSendMessage(text="\n".join(reply))
            )
            return