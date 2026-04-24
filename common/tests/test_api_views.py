from django.urls import reverse
from rest_framework import status


class TestCurrentWordAPIView:
    """Тесты для CurrentWordAPIView"""

    def test_unauthenticated_access(self, api_client):
        """Неавторизованный пользователь получает 401"""

        url = reverse("api_current_word")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_authenticated_no_session(self, api_client, student_user):
        """Авторизованный пользователь без сессии получает word: None"""

        api_client.force_authenticate(user=student_user)
        url = reverse("api_current_word")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["word"] is None

    def test_authenticated_with_session(self, api_client, student_user, review_session):
        """Авторизованный пользователь с сессией получает текущее слово"""

        api_client.force_authenticate(user=student_user)
        session = api_client.session
        session["review_queue"] = [w.id for w in review_session]
        session["review_current_index"] = 0
        session.save()

        url = reverse("api_current_word")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["word"] is not None
        assert response.data["word"]["id"] == review_session[0].id
        assert response.data["current_index"] == 1
        assert response.data["total_count"] == 3

    def test_session_completed(self, api_client, student_user):
        """Когда сессия завершена, возвращается word: None"""

        api_client.force_authenticate(user=student_user)
        session = api_client.session
        session["review_queue"] = []
        session["review_current_index"] = 0
        session.save()

        url = reverse("api_current_word")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["word"] is None


class TestProcessResultAPIView:
    """Тесты для ProcessResultAPIView"""

    def test_unauthenticated_access(self, api_client):
        """Неавторизованный пользователь получает 401"""

        url = reverse("api_process_result")
        response = api_client.post(url, {})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_know_result_updates_stage(self, api_client, student_user, user_word):
        """Результат "know" обновляет stage и удаляет слово из очереди"""

        api_client.force_authenticate(user=student_user)
        session = api_client.session
        session["review_queue"] = [user_word.id]
        session["review_current_index"] = 0
        session.save()

        url = reverse("api_process_result")
        data = {"user_word_id": user_word.id, "result": "know"}
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["session_complete"] is True

        user_word.refresh_from_db()
        assert user_word.stage == 1

    def test_dont_know_result_moves_to_end(self, api_client, student_user, review_session):
        """Результат 'dont_know' перемещает слово в конец очереди"""

        api_client.force_authenticate(user=student_user)
        session = api_client.session
        queue = [w.id for w in review_session]
        session["review_queue"] = queue.copy()
        session["review_current_index"] = 0
        session.save()

        url = reverse("api_process_result")
        data = {"user_word_id": queue[0], "result": "dont_know"}
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["session_complete"] is False

        updated_queue = api_client.session["review_queue"]
        assert updated_queue[-1] == queue[0]
        assert len(updated_queue) == 3

    def test_session_complete_after_all_words_known(self, api_client, student_user, user_word):
        """Сессия завершается после того, как все слова отмечены как "know" """

        api_client.force_authenticate(user=student_user)
        session = api_client.session
        session["review_queue"] = [user_word.id]
        session["review_current_index"] = 0
        session.save()

        url = reverse("api_process_result")
        data = {"user_word_id": user_word.id, "result": "know"}
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["session_complete"] is True
        assert "review_queue" not in api_client.session


class TestCheckPronunciationAPIView:
    """Тесты для CheckPronunciationAPIView"""

    def test_unauthenticated_access(self, api_client):
        """Неавторизованный пользователь получает 401"""
        url = reverse("api_check_pronunciation")
        response = api_client.post(url, {})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_correct_pronunciation(self, api_client, student_user, user_word):
        """Правильное произношение определяется корректно"""

        api_client.force_authenticate(user=student_user)
        url = reverse("api_check_pronunciation")
        data = {"user_word_id": user_word.id, "spoken_text": user_word.display_term}
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["is_correct"] is True
        assert "Отлично" in response.data["message"]

    def test_incorrect_pronunciation(self, api_client, student_user, user_word):
        """Неправильное произношение определяется корректно"""

        api_client.force_authenticate(user=student_user)
        url = reverse("api_check_pronunciation")
        data = {"user_word_id": user_word.id, "spoken_text": "wrong_term"}
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["is_correct"] is False

    def test_case_insensitive_match(self, api_client, student_user, user_word):
        """Проверка не чувствительна к регистру"""

        api_client.force_authenticate(user=student_user)
        url = reverse("api_check_pronunciation")
        data = {"user_word_id": user_word.id, "spoken_text": user_word.display_term.upper()}
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["is_correct"] is True

    def test_word_not_found(self, api_client, student_user):
        """Обработка несуществующего слова"""

        api_client.force_authenticate(user=student_user)
        url = reverse("api_check_pronunciation")
        data = {"user_word_id": 99999, "spoken_text": "test"}
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_invalid_data(self, api_client, student_user):
        """Невалидные данные возвращают 400"""

        api_client.force_authenticate(user=student_user)
        url = reverse("api_check_pronunciation")
        data = {}
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestCheckWrittenAnswerAPIView:
    """Тесты для CheckWrittenAnswerAPIView"""

    def test_correct_written_answer(self, api_client, student_user, user_word):
        """Правильный письменный ответ обновляет stage"""

        api_client.force_authenticate(user=student_user)
        initial_stage = user_word.stage

        url = reverse("api_check_written")
        data = {"user_word_id": user_word.id, "answer": user_word.display_term}
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["is_correct"] is True
        assert response.data["next_stage"] == initial_stage + 1

        user_word.refresh_from_db()
        assert user_word.stage == initial_stage + 1

    def test_incorrect_written_answer(self, api_client, student_user, user_word):
        """Неправильный письменный ответ сбрасывает stage"""

        user_word.stage = 3
        user_word.save()

        api_client.force_authenticate(user=student_user)
        url = reverse("api_check_written")
        data = {"user_word_id": user_word.id, "answer": "wrong_answer"}
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["is_correct"] is False
        assert response.data["next_stage"] == 0

        user_word.refresh_from_db()
        assert user_word.stage == 0

    def test_whitespace_handling(self, api_client, student_user, user_word):
        """Пробелы в начале и конце игнорируются"""

        api_client.force_authenticate(user=student_user)
        url = reverse("api_check_written")
        data = {"user_word_id": user_word.id, "answer": f"  {user_word.display_term}  "}
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["is_correct"] is True


class TestHideWordAPIView:
    """Тесты для HideWordAPIView"""

    def test_premium_user_can_hide_word(self, api_client, premium_user, user_word):
        """Premium пользователь может скрыть слово"""

        user_word.user = premium_user
        user_word.save()

        api_client.force_authenticate(user=premium_user)
        url = reverse("api_hide_word", kwargs={"user_word_id": user_word.id})
        response = api_client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True

        user_word.refresh_from_db()
        assert user_word.is_deleted_by_user is True

    def test_free_user_cannot_hide_word(self, api_client, student_user, user_word):
        """Обычный пользователь не может скрыть слово"""

        api_client.force_authenticate(user=student_user)
        url = reverse("api_hide_word", kwargs={"user_word_id": user_word.id})
        response = api_client.post(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

        user_word.refresh_from_db()
        assert user_word.is_deleted_by_user is False

    def test_cannot_hide_other_users_word(self, api_client, premium_user, user_word):
        """Нельзя скрыть слово другого пользователя"""

        api_client.force_authenticate(user=premium_user)
        url = reverse("api_hide_word", kwargs={"user_word_id": user_word.id})
        response = api_client.post(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestRestoreWordAPIView:
    """Тесты для RestoreWordAPIView"""

    def test_premium_user_can_restore_word(self, api_client, premium_user, user_word):
        """Premium пользователь может восстановить скрытое слово"""

        user_word.user = premium_user
        user_word.is_deleted_by_user = True
        user_word.save()

        api_client.force_authenticate(user=premium_user)
        url = reverse("api_restore_word", kwargs={"user_word_id": user_word.id})
        response = api_client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True

        user_word.refresh_from_db()
        assert user_word.is_deleted_by_user is False

    def test_free_user_cannot_restore_word(self, api_client, student_user, user_word):
        """Обычный пользователь не может восстановить слово"""

        user_word.is_deleted_by_user = True
        user_word.save()

        api_client.force_authenticate(user=student_user)
        url = reverse("api_restore_word", kwargs={"user_word_id": user_word.id})
        response = api_client.post(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestWordDetailAPIView:
    """Тесты для WordDetailAPIView"""

    def test_get_word_detail(self, api_client, student_user, user_word):
        """Получение детальной информации о слове"""

        api_client.force_authenticate(user=student_user)
        url = reverse("api_word_detail", kwargs={"word_id": user_word.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["term"] == user_word.display_term
        assert "transcription" in response.data
        assert "image" in response.data
