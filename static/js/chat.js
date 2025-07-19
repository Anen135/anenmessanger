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

    $('#messages').empty(); // Очищаем перед добавлением новой истории

    messages.forEach(function(message) {
        let contentHtml = '';

        if (message.is_file) {
            if (message.file_type === 'image/png') {
                contentHtml = `
                    <div class="file-message">
                        <p><strong>Файл:</strong> <a href="static/${message.file_path}" download>${message.file_name}</a></p>
                        <img src="static/${message.file_path}" alt="File" class="me-2" width="100%">
                        <p><small>${message.file_type}, ${Math.round(message.file_size / 1024)} KB</small></p>
                    </div>
                `;
            } else if (message.file_type === 'application/x-zip-compressed') {
                contentHtml = `
                    <div class="file-message">
                        <p><strong>Файл:</strong> <a href="static/${message.file_path}" download>${message.file_name}</a></p>
                        <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="currentColor" class="bi bi-file-earmark-zip" viewBox="0 0 16 16">
                        <path d="M5 7.5a1 1 0 0 1 1-1h1a1 1 0 0 1 1 1v.938l.4 1.599a1 1 0 0 1-.416 1.074l-.93.62a1 1 0 0 1-1.11 0l-.929-.62a1 1 0 0 1-.415-1.074L5 8.438zm2 0H6v.938a1 1 0 0 1-.03.243l-.4 1.598.93.62.929-.62-.4-1.598A1 1 0 0 1 7 8.438z"/>
                        <path d="M14 4.5V14a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V2a2 2 0 0 1 2-2h5.5zm-3 0A1.5 1.5 0 0 1 9.5 3V1h-2v1h-1v1h1v1h-1v1h1v1H6V5H5V4h1V3H5V2h1V1H4a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1V4.5z"/>
                        </svg>
                        <p><small>${message.file_type}, ${Math.round(message.file_size / 1024)} KB</small></p>
                    </div>
                `;
            }
        } else {
            // Обычное текстовое сообщение
            contentHtml = `<p class="mb-0">${message.content}</p>`;
        }

        $('#messages').append(
            '<div class="d-flex align-items-start">' +  // Контейнер с выравниванием по верху
                '<div class="flex-grow-1">' +
                    '<div class="d-flex align-items-center">' +  // Горизонтальное выравнивание имени и кнопки
                        '<strong>' + message.sender_username + ':</strong>' +
                        '<button class="ml-2 delete-message btn p-0" data-message-id="' + message.id + '">' +
                            '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#ff0000" class="bi bi-trash" viewBox="0 0 16 16">' +
                                '<path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"/>' +
                                '<path fill-rule="evenodd" d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4L4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z"/>' +
                            '</svg>' +
                        '</button>' +
                    '</div>' +
                    '<div class="message-content">' +  // Контент сообщения
                        contentHtml +
                    '</div>' +
                '</div>' +
            '</div>'
        );
    });

    $('[data-toggle="popover"]').popover({ trigger: 'click', container: 'body' });
    $('#messages').scrollTop($('#messages')[0].scrollHeight);
});
 


// Функция для отправки сообщения
function sendMessage() {
    const messageContent = $('#message-input').val();
    const messageType = $('#code-inpput').val();
    
    // Получаем id чата или группы
    const chatId = $('#chat-list .nav-link.active').data('chat-id');
    const chatType = $('#chat-list .nav-link.active').data('chat-type'); // personal или group

    // Использовать JS?
    const useJS = $('#code-input').is(':checked');

    if (messageContent) {
        // Отправляем сообщение через WebSocket
        socket.emit('send_message', {
            receiver_id: chatId,
            message_content: messageContent,
            chat_type: chatType,
            message_type: messageType,
            usejs: useJS
        });

        // Очищаем поле ввода
        $('#message-input').val('');
    }
}


$('#file-upload').on('change', function(e) {
    // Получаем файл непосредственно из текущего элемента
    const file = this.files[0];
    
    if (!file) {
        alert('Выберите файл');
        return;
    }

    // Проверка размера файла (например, до 10MB)
    if (file.size > 10 * 1024 * 1024) {
        alert('Файл слишком большой! Максимальный размер: 10MB');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    // Показываем индикатор загрузки
    $('#file-upload').prop('disabled', true);
    $('.file-upload-label').text('Загрузка...');

    // 1. Сначала отправим файл на сервер через HTTP
    $.ajax({
        url: '/upload',
        method: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            if (response.error) {
                alert('Ошибка при загрузке файла: ' + response.error);
                return;
            }

            // 2. После успешной загрузки — отправим WebSocket сообщение
            const activeChat = $('#chat-list .nav-link.active');
            if (activeChat.length === 0) {
                alert('Выберите чат для отправки файла');
                return;
            }

            const chatId = activeChat.data('chat-id');
            const chatType = activeChat.data('chat-type'); // personal или group

            socket.emit('send_file', {
                receiver_id: chatId,
                chat_type: chatType,
                file_data: {
                    filename: response.filename,
                    file_path: response.file_path,
                    file_type: response.file_type,
                    file_size: response.file_size
                }
            });
        },
        error: function(xhr, status, error) {
            alert('Ошибка при загрузке файла: ' + error + ' (' + status + ')' + xhr.responseText);
        },
        complete: function() {
            // Восстанавливаем состояние
            $('#file-upload').val('').prop('disabled', false);
            $('.file-upload-label').text('Выбрать файл');
        }
    });
});



// Обработчик для отправки сообщения по кнопке
$('#send-button').click(function() {
    sendMessage();
});

// Обработчик для отправки сообщения при нажатии клавиши Enter
$('#message-input').keypress(function(event) {
    if (event.which === 13) {  
        event.preventDefault();  
        sendMessage();  
    }
});

// Функция для прокрутки вниз
function scrollToBottom() {
    const messagesContainer = $('#messages');
    setTimeout(function() {
        messagesContainer.scrollTop(messagesContainer[0].scrollHeight);
    }, 50); // Немного задерживаем прокрутку, чтобы DOM успел обновиться
}

// Проверка, если пользователь находится внизу чата
function isScrolledToBottom() {
    const messagesContainer = $('#messages');
    return messagesContainer[0].scrollHeight - messagesContainer.scrollTop() === messagesContainer.outerHeight();
}

$(document).on('click', '.delete-message', function() {
    const messageId = $(this).data('message-id');
    const chatType = $('#chat-list .nav-link.active').data('chat-type');
    deleteMessage(messageId, chatType);
});

// Функция для удаления сообщения
function deleteMessage(messageId, chatType) {
    // Отправляем запрос на сервер через WebSocket
    // Проверяем, что пользователь подтверждает удаление
    if (!confirm('Вы действительно хотите удалить это сообщение?')) {
        return;
    }

    // Отправляем запрос на сервер через WebSocket
    socket.emit('delete_message', {
        message_id: messageId,
        chat_type: chatType
    }, function(response) {
        if (response === false) {
            alert('Не удалось удалить сообщение. Возможно, у вас нет прав.');
        }
    });
}

// Обработчик события удаления сообщения от сервера
socket.on('message_deleted', function(data) {
    const messageId = data.message_id;
    
    // Находим элемент сообщения в DOM
    const messageElement = $(`[data-message-id="${messageId}"]`);
    
    if (messageElement.length) {
        // Создаем эффект удаления
        messageElement.fadeOut(300, function() {
            $(this).remove();
            
            // Обновляем интерфейс, если нужно
            if ($('#messages').children().length === 0) {
                $('#messages').html('<p class="text-muted">Нет сообщений</p>');
            }
        });
    }
});


socket.on('new_message', function(message) {
    let contentHtml = '';
    
    // Проверяем, является ли сообщение файлом
    if (message.is_file) {
        if (message.file_type.startsWith('image/')) {
            // Для изображений показываем превью
            contentHtml = `
                <div class="file-message">
                    <p><strong>Файл:</strong> <a href="/static/${message.file_path}" download>${message.file_name}</a></p>
                    <img src="/static/${message.file_path}" alt="File" class="me-2" width="100%">
                    <p><small>${message.file_type}, ${Math.round(message.file_size / 1024)} KB</small></p>
                </div>
            `;
        } else {
            // Для других типов файлов просто ссылка
            contentHtml = `
                <div class="file-message">
                    <p><strong>Файл:</strong> <a href="/static/${message.file_path}" download>${message.file_name}</a></p>
                    <p><small>${message.file_type}, ${Math.round(message.file_size / 1024)} KB</small></p>
                </div>
            `;
        }
    } else {
        // Обычное текстовое сообщение
        contentHtml = `<p class="mb-0">${message.content}</p>`;
    }

    // Создаем элемент сообщения
    const messageElement = $(
        '<div class="message align-items-center mb-2 d-flex" data-message-id="' + message.id + '">' +
            '<div class="mr-4">' +
                '<img src="/avatars/' + message.sender_avatar + '" alt="Avatar" class="message-avatar me-2" ' +
                     'data-toggle="popover" data-title="' + message.sender_username + '" ' + 
                     'data-content="' + (message.sender_about || '*У пользователя нет описания*') + '" ' + 
                     'data-placement="top" id="popover-img-' + message.sender_username + '">' +
            '</div>' +
            '<div>' +
                '<strong>' + message.sender_username + ':</strong>' +
                contentHtml +
            '</div>' +
        '</div>'
    );

    // Добавляем сообщение в чат
    $('#messages').append(messageElement);
    
    // Инициализируем popover
    $('[data-toggle="popover"]').popover({ trigger: 'click', container: 'body' });
    
    // Прокручиваем вниз, если это наше сообщение
    if (message.self_send) {
        $('#messages').scrollTop($('#messages')[0].scrollHeight);
    }
    
    console.log('New message:', message);
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


// Обработчик нажатия на кнопку удаления друга
$('.delete-chat-btn').on('click', function() {
    var chatId = $(this).data('chat-id');  // Получаем ID чата
    // Отправляем запрос на сервер для удаления друга через WebSocket
    socket.emit('remove_friend', {
        'friend_id': chatId
    });
});
// Обрабатываем ответ от сервера
socket.on('remove_friend_response', function(response) {
    if (response.success) {
        // Если операция успешна, удаляем элемент из списка
        $('#chat-' + chatId).closest('li').remove();
    } else if (response.error) {
        // Если ошибка, показываем сообщение
        alert(response.error);
    }
});
