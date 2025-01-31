// Устанавливаем соединение с WebSocket
const socket = io.connect(window.location.origin);

// При клике на чат (личный или групповой) загружаем историю сообщений
$(document).on('click', '.chat_button', function () {
    const chatId = $(this).data('chat-id');
    const chatType = $(this).data('chat-type'); // friend или group

    // Очищаем окно сообщений
    $('#messages').empty();

    // Запрашиваем историю сообщений
    socket.emit('get_chat_history', { chat_id: chatId, chat_type: chatType });
});

// Обработка получения истории сообщений
socket.on('chat_history', function (data) {
    if (data.error) {
        $('#messages').html('<p class="error-message">' + data.error + '</p>');
        return;
    }

    // Очищаем окно сообщений
    $('#messages').empty();

    // Добавляем сообщения в окно
    data.messages.forEach(function (message) {
        $('#messages').append(
            '<p><strong>' + message.sender_username + ':</strong> ' + message.content + '</p>'
        );
    });
});

// Обработка ошибок при получении истории
socket.on('chat_history_error', function (error) {
    alert(error.error);
});


$('#chat-list').on('click', '.chat_button', function() {
    // Убираем класс active с других чатов
    $('#chat-list .chat_button').removeClass('active');
    
    // Добавляем класс active к текущему чату
    $(this).addClass('active');
});

$('#send-button').on('click', function () {
    const messageContent = $('#message-input').val();
    const activeChat = $('#chat-list .chat_button.active');

    // Получаем ID и тип текущего чата
    const chatId = activeChat.data('chat-id');
    const chatType = activeChat.data('chat-type'); // friend или group

    if (!chatId || !messageContent) {
        alert("Выберите чат и введите сообщение.");
        return;
    }

    // Отправляем сообщение через WebSocket
    socket.emit('send_message', {
        chat_id: chatId,
        chat_type: chatType,
        message_content: messageContent
    });

    // Очищаем поле ввода
    $('#message-input').val('');
});


$('#create-group-button').on('click', function () {
    const groupName = prompt('Введите название группы:');
    if (groupName) {
        $.ajax({
            url: '/create_group',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ group_name: groupName }),
            success: function (data) {
                if (data.success) {
                    alert('Группа успешно создана!');
                } else {
                    alert(`Ошибка: ${data.message}`);
                }
            },
            error: function (xhr, status, error) {
                console.error('Ошибка:', error);
            }
        });
    }
});

// Обработчик успешной отправки сообщения
socket.on('new_message', function(message) {
    // Добавляем новое сообщение в окно чата
    $('#messages').append(
        '<p><strong>' + message.sender_username + ':</strong> ' + message.content + '</p>'
    );
});
