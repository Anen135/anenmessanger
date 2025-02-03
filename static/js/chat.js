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
                    '<img src="avatars/' + message.sender_avatar + '" alt="Avatar" class="message-avatar me-2" ' +
                         'data-toggle="popover" data-title="' + message.sender_username + '" ' + 
                         'data-content="' + message.sender_about + '" ' + 
                         'data-placement="top" id="popover-img-' + message.sender_username + '">' +
                '</div>' +
                '<div>' +
                    '<strong>' + message.sender_username + ':</strong>' +
                    '<p class="mb-0">' + message.content + '</p>' +
                '</div>' +
            '</div>'
        );
    });
    // Инициализация popover для каждого нового сообщения
    $('[data-toggle="popover"]').popover({ trigger: 'click', container: 'body' });
});


// Функция для отправки сообщения
function sendMessage() {
    const messageContent = $('#message-input').val();
    const messageType = $('#code-inpput').val();
    
    // Получаем id чата или группы
    const chatId = $('#chat-list .nav-link.active').data('chat-id');
    const chatType = $('#chat-list .nav-link.active').data('chat-type'); // personal или group

    if (messageContent) {
        // Отправляем сообщение через WebSocket
        socket.emit('send_message', {
            receiver_id: chatId,
            message_content: messageContent,
            chat_type: chatType,
            message_type: messageType
        });

        // Очищаем поле ввода
        $('#message-input').val('');
    }
}

// Обработчик для отправки сообщения по кнопке
$('#send-button').click(function() {
    sendMessage();
});

// Обработчик для отправки сообщения при нажатии клавиши Enter
$('#message-input').keypress(function(event) {
    if (event.which === 13) {  // Проверяем, была ли нажата клавиша Enter (код 13)
        event.preventDefault();  // Отменяем стандартное поведение (например, отправка формы)
        sendMessage();  // Отправляем сообщение
    }
});

// Обработчик успешной отправки сообщения
socket.on('new_message', function(message) {
    // Добавляем новое сообщение в окно чата
    $('#messages').append(
        '<div class="message align-items-center mb-2 d-flex">' +
            '<div class="mr-4">' +
                '<img src="avatars/' + message.sender_avatar + '" alt="Avatar" class="message-avatar me-2" ' +
                     'data-toggle="popover" data-title="' + message.sender_username + '" ' + 
                     'data-content="' + message.sender_about + '" ' + 
                     'data-placement="top" id="popover-img-' + message.sender_username + '">' +
            '</div>' +
            '<div>' +
                '<strong>' + message.sender_username + ':</strong>' +
                '<p class="mb-0">' + message.content + '</p>' +
            '</div>' +
        '</div>'
    );
    $('[data-toggle="popover"]').popover({ trigger: 'click', container: 'body' });
});

// Обработчик клика по кнопке "Выйти из группы"
$(document).on('click', '.leave-group-btn', function() {
    var groupId = $(this).data('group-id');

    // Подтверждение выхода из группы
    if (confirm('Вы уверены, что хотите выйти из этой группы?')) {
        // Отправка события на сервер
        socket.emit('leave_group', { group_id: groupId });
    }
});

// Обработчик ответа от сервера
socket.on('leave_group_response', function(response) {
    if (response.success) {
        alert(response.message);
        // Удаление группы из списка чатов
        $('button.leave-group-btn[data-group-id="' + response.group_id + '"]').closest('li').remove();
    } else {
        alert('Ошибка: ' + (response.error || 'Неизвестная ошибка'));
    }
});
