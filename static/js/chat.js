// Устанавливаем соединение с WebSocket
const socket = io.connect(window.location.origin);

// Обработчик клика на чат
$(document).on('click', '.nav-link', function() {
    // Получаем ID чата (друга)
    const chatId = $(this).data('chat-id');
    
    // Отправляем запрос на сервер для получения истории чата
    socket.emit('get_chat_history', { chat_id: chatId });
    
    // Очищаем окно сообщений
    $('#messages').empty();
});

$('#chat-list').on('click', '.nav-link', function() {
    // Убираем класс active с других чатов
    $('#chat-list .nav-link').removeClass('active');
    
    // Добавляем класс active к текущему чату
    $(this).addClass('active');
});


// Обработчик получения истории чата
socket.on('chat_history', function(messages) {
    // Если есть ошибки, выводим их
    if (messages.error) {
        $('#messages').html('<p class="error-message">' + messages.error + '</p>');
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
$('#send-button').on('click', function() {
    const messageContent = $('#message-input').val();

    // Получаем текущего собеседника через контекст this (элемент, на который был клик)
    const receiverId = $('#chat-list .nav-link.active').data('chat-id'); 

    // Проверяем, есть ли receiverId
    if (!receiverId) {
        alert("Выберите собеседника для отправки сообщения.");
        return;
    }

    // Отправляем сообщение через WebSocket
    socket.emit('send_message', {
        receiver_id: receiverId,
        message_content: messageContent
    });

    // Очищаем поле ввода
    $('#message-input').val('');
});



// Обработчик успешной отправки сообщения
socket.on('new_message', function(message) {
    // Добавляем новое сообщение в окно чата
    $('#messages').append(
        '<p><strong>' + message.sender_username + ':</strong> ' + message.content + '</p>'
    );

});
