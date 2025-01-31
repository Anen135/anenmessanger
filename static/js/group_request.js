$(document).ready(function () {
    // Открытие модального окна для создания группы
    $('#create-group-button').click(function () {
        $('#groupModal').modal('show');
    });

    // Отправка запроса на вступление в группу через AJAX
    $('#confirm-send-group-request').click(function () {
        const groupId = $('#group-id').val(); // Получение ID группы из модального окна
        if (groupId) {
            $.ajax({
                url: '/send_group_request',
                type: 'POST',
                data: { group_id: groupId },
                success: function (response) {
                    if (response.success) {
                        alert('Запрос на вступление в группу отправлен!');
                        $('#groupModal').modal('hide');
                    } else {
                        alert(response.message);
                    }
                },
                error: function () {
                    alert('Ошибка отправки запроса.');
                }
            });
        } else {
            alert('Пожалуйста, введите ID группы.');
        }
    });

    // Получение запросов в группу через AJAX
    $('#show-group-requests-button').click(function () {
        $.ajax({
            url: '/get_group_requests',
            type: 'GET',
            success: function (response) {
                if (response.success) {
                    // Очистка предыдущих запросов
                    $('#group-requests-list').empty();

                    // Добавление новых запросов
                    response.incoming_requests.forEach(function (request) {
                        $('#group-requests-list').append(
                            `<li>${request.user_username} хочет вступить в группу "${request.group_name}"
                                <button class="btn btn-sm btn-success" onclick="respondGroupRequest(${request.id}, 'accept')">Принять</button>
                                <button class="btn btn-sm btn-danger" onclick="respondGroupRequest(${request.id}, 'decline')">Отклонить</button>
                            </li>`
                        );
                    });

                    response.outgoing_requests.forEach(function (request) {
                        $('#group-requests-list').append(
                            `<li>Вы отправили запрос в группу "${request.group_name}"
                                <button class="btn btn-sm btn-danger" onclick="cancelGroupRequest(${request.id})">Отменить</button>
                            </li>`
                        );
                    });

                    $('#groupRequestsModal').modal('show');
                } else {
                    alert(response.message);
                }
            },
            error: function () {
                alert('Ошибка при получении запросов.');
            }
        });
    });
});

// Принятие или отклонение запроса на вступление в группу
function respondGroupRequest(requestId, action) {
    $.ajax({
        url: `/respond_group_request/${requestId}/${action}`,
        type: 'POST',
        success: function (response) {
            if (response.success) {
                alert(response.message);
                $('#show-group-requests-button').click(); // Обновляем список запросов
            } else {
                alert(response.message);
            }
        },
        error: function () {
            alert('Ошибка обработки запроса.');
        }
    });
}

// Отмена исходящего запроса в группу
function cancelGroupRequest(requestId) {
    $.ajax({
        url: `/respond_group_request/${requestId}/cancel`,
        type: 'POST',
        success: function (response) {
            if (response.success) {
                alert(response.message);
                $('#show-group-requests-button').click(); // Обновляем список запросов
            } else {
                alert(response.message);
            }
        },
        error: function () {
            alert('Ошибка отмены запроса.');
        }
    });
}
