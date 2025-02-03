$(document).ready(function() {
    // Открытие модального окна для отправки запроса в друзья
    $('#send-friend-request').click(function() {
        $('#nicknameModal').modal('show');
    });

    // Отправка запроса в друзья через AJAX
    $('#confirm-send-request').click(function() {
        const username = $('#friend-username').val();
        if (username) {
            $.ajax({
                url: '/send_friend_request',
                type: 'POST',
                data: { 'friend_username': username },
                success: function(response) {
                    if (response.success) {
                        alert('Запрос отправлен!');
                        $('#nicknameModal').modal('hide');
                    } else {
                        alert(response.message);
                    }
                },
                error: function() {
                    alert('Ошибка отправки запроса.');
                }
            });
        } else {
            alert('Пожалуйста, введите никнейм.');
        }
    });

    // Удалить из друзей
    $('#remove-from-friends').click(function() {
        const friendId = $(this).data('friend-id');
        if (!friendId) {
            alert('Неизвестный пользователь.');
            return;
        }
        $.ajax({
            url: '/remove_from_friends',
            type: 'POST',
            data: { 'friend_id': friendId },
            success: function(response) {
                if (response.success) {
                    alert('Пользователь удален из друзей!');
                    location.reload();
                } else {
                    alert(response.message);
                }
            },
            error: function() {
                alert('Ошибка при удалении из друзей.');
            }
        })
    })

    // Получение запросов в друзья через AJAX
    $('#show-requests-button').click(function() {
        $.ajax({
            url: '/get_friend_requests',
            type: 'GET',
            success: function(response) {
                if (response.success) {
                    // Очистка предыдущих запросов
                    $('#friend-requests-list').empty();
                    
                    // Добавление новых запросов
                    response.incoming_requests.forEach(function(request) {
                        $('#friend-requests-list').append(
                            '<li>' + request.sender_username + ` <button class="btn btn-sm btn-success" onclick="respondFriendRequest(${request.id}, 'accept')">Принять</button> <button class="btn btn-sm btn-danger" onclick="declineRequest(${request.id})">Отклонить</button></li>`
                        );
                    });

                    response.outgoing_requests.forEach(function(request) {
                        $('#friend-requests-list').append(
                            '<li>' + request.receiver_username + ` <button class="btn btn-sm btn-danger" onclick="respondFriendRequest(${request.id}, 'cancel')">Отменить</button></li>`
                        );
                    });

                    $('#requestsModal').modal('show');
                } else {
                    alert(response.message);
                }
            },
            error: function() {
                alert('Ошибка при получении запросов.');
            }
        });
    });

    // Отправка сообщения в чат через AJAX
    $('#send-button').click(function() {
        const messageContent = $('#message-input').val();
        if (messageContent) {
            $.ajax({
                url: '/send_message',
                type: 'POST',
                data: { 'message_content': messageContent },
                success: function(response) {
                    if (response.success) {
                        $('#messages').append('<p><strong>' + response.sender + ':</strong> ' + messageContent + '</p>');
                        $('#message-input').val('');
                    } else {
                        alert('Ошибка отправки сообщения.');
                    }
                },
                error: function() {
                    alert('Ошибка отправки сообщения.');
                }
            });
        }
    });
});

function respondFriendRequest(requestId, action) {
    $.ajax({
        url: `/respond_friend_request/${requestId}/${action}`,
        type: 'GET',
        success: function(response) {
            if (response.success) {
                alert(action === 'accept' ? 'Запрос принят!' : 'Запрос отклонен!');
                $('#requestsModal').modal('hide');
            } else {
                alert('Ошибка при обработке запроса.');
            }
        },
        error: function() {
            alert('Ошибка при обработке запроса.');
        }
    });
}

function cancelRequest(requestId) {
    $.ajax({
        url: '/respond_friend_request/' + requestId + '/decline',
        type: 'GET',
        success: function(response) {
            if (response.success) {
                alert('Запрос отменен!');
                $('#requestsModal').modal('hide');
            } else {
                alert('Ошибка при отмене запроса.');
            }
        },
        error: function() {
            alert('Ошибка при отмене запроса.');
        }
    });
}
