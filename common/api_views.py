from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from vocabulary.models import UserWord
from .serializers import (
    UserWordSerializer,
    PronunciationCheckSerializer,
    WrittenAnswerSerializer,
)


class CurrentWordAPIView(APIView):
    """API для текущего слова"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queue = request.session.get("review_queue", [])
        current_index = request.session.get("review_current_index", 0)

        if current_index >= len(queue):
            return Response({'word': None})

        user_word = UserWord.objects.get(id=queue[current_index])
        serializer = UserWordSerializer(user_word)

        return Response({
            "word": serializer.data,
            "current_index": current_index + 1,
            "total_count": len(queue)
        })


class ProcessResultAPIView(APIView):
    """API для статуса слова в очереди"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_word_id = request.data.get("user_word_id")
        result = request.data.get("result")

        queue = request.session.get("review_queue", [])
        current_index = request.session.get("review_current_index", 0)

        if current_index >= len(queue):
            return Response({"session_complete": True})

        if result == "know":
            # Слово выучено → удаляем из очереди
            queue.pop(current_index)
            # Обновляем stage
            try:
                user_word = UserWord.objects.get(id=user_word_id, user=request.user)
                user_word.update_stage(True)
            except UserWord.DoesNotExist:
                pass
            # current_index не меняется (следующее слово сдвинулось на его место)
        else:
            # Слово не выучено → перемещаем в КОНЕЦ очереди СРАЗУ
            word_id = queue.pop(current_index)
            queue.append(word_id)  # ← добавляем в конец
            # Обновляем stage
            try:
                user_word = UserWord.objects.get(id=user_word_id, user=request.user)
                user_word.update_stage(False)
            except UserWord.DoesNotExist:
                pass
            # current_index не меняется (следующее слово на его месте)

        # Проверяем, не закончилась ли сессия
        if not queue:
            # Сессия завершена
            for key in ["review_queue", "review_current_index"]:
                if key in request.session:
                    del request.session[key]
            return Response({"session_complete": True})

        # Сохраняем обновлённые данные
        request.session["review_queue"] = queue
        request.session["review_current_index"] = current_index

        return Response({"session_complete": False})


class CheckPronunciationAPIView(APIView):
    """API для проверки произношения"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PronunciationCheckSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user_word_id = serializer.validated_data["user_word_id"]
        spoken_text = serializer.validated_data["spoken_text"]

        try:
            user_word = UserWord.objects.get(id=user_word_id, user=request.user)
            expected_term = user_word.display_term.lower().strip()
            is_correct = expected_term == spoken_text.lower().strip()

            return Response({
                "success": True,
                "is_correct": is_correct,
                "message": "Отлично! ✓" if is_correct else "Попробуйте ещё раз ✗"
            })
        except UserWord.DoesNotExist:
            return Response({"error": "Слово не найдено"}, status=status.HTTP_404_NOT_FOUND)


class CheckWrittenAnswerAPIView(APIView):
    """API для проверки письменного ответа"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = WrittenAnswerSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user_word_id = serializer.validated_data["user_word_id"]
        written_answer = serializer.validated_data["answer"]

        try:
            user_word = UserWord.objects.get(id=user_word_id, user=request.user)
            expected_term = user_word.display_term.lower().strip()
            is_correct = expected_term == written_answer.lower().strip()

            # Обновляем stage
            user_word.update_stage(is_correct)

            return Response({
                "success": True,
                "is_correct": is_correct,
                "next_stage": user_word.stage
            })
        except UserWord.DoesNotExist:
            return Response({"error": "Слово не найдено"}, status=status.HTTP_404_NOT_FOUND)


class HideWordAPIView(APIView):
    """API для скрытия слова (только Premium)"""

    permission_classes = [IsAuthenticated]

    def post(self, request, user_word_id):
        if request.user.subscription_type != "premium":
            return Response({"error": "Доступно только для Premium"}, status=status.HTTP_403_FORBIDDEN)

        try:
            user_word = UserWord.objects.get(id=user_word_id, user=request.user)
            user_word.is_deleted_by_user = True
            user_word.save()
            return Response({"success": True})
        except UserWord.DoesNotExist:
            return Response({"error": "Слово не найдено"}, status=status.HTTP_404_NOT_FOUND)


class RestoreWordAPIView(APIView):
    """API для восстановления слова (только Premium)"""

    permission_classes = [IsAuthenticated]

    def post(self, request, user_word_id):
        if request.user.subscription_type != "premium":
            return Response({"error": "Доступно только для Premium"}, status=status.HTTP_403_FORBIDDEN)

        try:
            user_word = UserWord.objects.get(id=user_word_id, user=request.user)
            user_word.is_deleted_by_user = False
            user_word.save()
            return Response({"success": True})
        except UserWord.DoesNotExist:
            return Response({"error": "Слово не найдено"}, status=status.HTTP_404_NOT_FOUND)


class WordDetailAPIView(APIView):
    """API для детальной информации слова"""

    permission_classes = [IsAuthenticated]

    def get(self, request, word_id):
        user_word = UserWord.objects.get(id=word_id, user=request.user)
        return Response({
            "term": user_word.display_term,
            "transcription": user_word.display_transcription,
            "image": user_word.display_image,
            "audio": user_word.word.audio_url if user_word.word else None
        })
