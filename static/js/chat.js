// Устанавливаем соединение с WebSocket
const socket = io.connect(window.location.origin);


// Обработчик клика на чат (групповой или личный)
$(document).on('click', '.nav-link', function() {
    const chatId = $(this).data('chat-id');
    const chatType = $(this).data('chat-type');  // Получаем тип чата (personal или group)

    // Убираем класс active у всех ссылок
    $('.nav-link').removeClass('active');

    // Добавляем класс active к текущему чату
    $(this).addClass('active');

    // Отправляем запрос на сервер для получения истории чата
    socket.emit('get_chat_history', { chat_id: chatId, chat_type: chatType });

    // Очищаем окно сообщений
    $('#messages').empty();
});

socket.on('chat_history', function(data) {
    const messages = data.messages;

    if (data.error) {
        $('#messages').html('<p class="error-message">' + data.error + '</p>');
        return;
    }

    // Заполняем окно сообщениями из истории
    messages.forEach(function(message) {
        $('#messages').append(
            '<div class="message align-items-center mb-2 d-flex">' +
                '<div class="mr-4">' +
                    '<img src="avatars/' + message.sender_avatar + '" alt="Avatar" class="message-avatar me-2">' +
                '</div>' +
                '<div>' +
                    '<strong>' + message.sender_username + ':</strong>' +
                    '<p class="mb-0">' + message.content + '</p>' +
                '</div>' +
            '</div>'
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
        '<div class="message align-items-center mb-2 d-flex">' +
        '<div class="mr-4">' +
            '<img src="avatars/' + message.sender_avatar + '" alt="Avatar" class="message-avatar me-2">' +
        '</div>' +
        '<div>' +
            '<strong>' + message.sender_username + ':</strong>' +
            '<p class="mb-0">' + message.content + '</p>' +
        '</div>' +
    '</div>'
    );
});

