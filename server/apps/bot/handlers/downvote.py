from asgiref.sync import sync_to_async
from aiogram import Router, types
from django.db.models import F

from server.apps.bot.keyboards.downvote_kb import DownvoteCallbackFactory
from server.apps.core.models import MediaIncident

router = Router()


@router.callback_query(DownvoteCallbackFactory.filter())
async def downvote_callback(
    callback: types.CallbackQuery, callback_data: DownvoteCallbackFactory
):
    await callback.answer()

    @sync_to_async
    def update_downvote():
        MediaIncident.objects.filter(id=callback_data.incident_type_id).update(
            downvote=F("downvote") + 1
        )

    await update_downvote()
    await callback.message.delete_reply_markup()
