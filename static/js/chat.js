// Устанавливаем соединение с WebSocket
const socket = io.connect(window.location.origin);


// Обработчик клика на чат (групповой или личный)
$(document).on('click', '.nav-link', function() {
    const chatId = $(this).data('chat-id');
    const chatType = $(this).data('chat-type');  // Получаем тип чата (personal или group)

    // Отправляем запрос на сервер для получения истории чата
    socket.emit('get_chat_history', { chat_id: chatId, chat_type: chatType });
    // Очищаем окно сообщений
    $('#messages').empty();
});

// Обработчик получения истории чата (группового или личного)
socket.on('chat_history', function(data) {
    const messages = data.messages;

    if (data.error) {
        $('#messages').html('<p class="error-message">' + data.error + '</p>');
        return;
    }

    // Заполняем окно сообщениями из истории
    messages.forEach(function(message) {
        $('#messages').append(
            '<p><strong>' + message.sender_username + ':</strong> ' + message.content + '</p>'
        );
    });
});


// Обработчик получения истории чата (группового или личного)
socket.on('chat_history', function(data) {
    const messages = data.messages;

    if (data.error) {
        $('#messages').html('<p class="error-message">' + data.error + '</p>');
        return;
    }

    // Очищаем окно сообщений
    $('#messages').empty();

    // Заполняем окно сообщениями из истории
    messages.forEach(function(message) {
        $('#messages').append(
            '<p><strong>' + message.sender_username + ':</strong> ' + message.content + '</p>'
        );
    });
});

// Обработчик отправки сообщений
$('#send-button').click(function() {
    const messageContent = $('#message-input').val();
    
    // Получаем id чата или группы
    const chatId = $('#chat-list .nav-link.active').data('chat-id');
    const chatType = $('#chat-list .nav-link.active').data('chat-type'); // personal или group

    if (messageContent) {
        // Отправляем сообщение через WebSocket
        socket.emit('send_message', {
            receiver_id: chatId,
            message_content: messageContent,
            chat_type: chatType
        });

        // Очищаем поле ввода
        $('#message-input').val('');
    }
});





// Обработчик успешной отправки сообщения
socket.on('new_message', function(message) {
    // Добавляем новое сообщение в окно чата
    $('#messages').append(
        '<p><strong>' + message.sender_username + ':</strong> ' + message.content + '</p>'
    );
});

