$(document).ready(function() {
    // Обработчик клика на кнопку "Создать группу"
    $('#create-group-button').on('click', function() {
        // Открытие модального окна для создания группы
        $('#createGroupModal').modal('show');
    });
    // Обработчик события для кнопки создания группы
    $('#confirmCreateGroup').click(function() {
        // Получаем имя группы из поля ввода
        var groupName = $('#groupName').val().trim();

        // Если имя группы пустое, показываем ошибку
        if (!groupName) {
            $('#createGroupError').text('Пожалуйста, введите имя группы.').removeClass('d-none');
            return;
        }

        // Отправляем запрос на сервер через сокеты
        socket.emit('create_group', { name: groupName });

        // Очистка поля ввода и скрытие ошибки
        $('#createGroupError').addClass('d-none');
        $('#groupName').val('');
    });

    // Обработчик ответа от сервера
    socket.on('create_group_response', function(data) {
        if (data.error) {
            // Если произошла ошибка, выводим сообщение об ошибке
            $('#createGroupError').text(data.error).removeClass('d-none');
        } else if (data.success) {
            // Если группа была успешно создана, закрываем модальное окно
            $('#createGroupModal').modal('hide');

            // Выводим уведомление об успешном создании
            alert(data.message);

            // Здесь можно добавить логику для обновления UI или перехода в чат группы
        }
    });
});

    
