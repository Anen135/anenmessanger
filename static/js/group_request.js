// Обработчик клика по кнопке "+" для добавления пользователей в группу
$(document).on('click', '.add-user-btn', function () {
    const groupId = $(this).data('group-id');

    // Устанавливаем groupId в модальное окно
    $('#add-user-modal').data('group-id', groupId);

    // Открыть модальное окно для добавления пользователей в группу
    $('#add-user-modal').modal('show');

    // Пример отправки запроса на сервер для получения списка пользователей, которых можно добавить
    $.ajax({
        url: '/get_users_for_group',
        method: 'GET',
        data: { group_id: groupId },
        success: function (response) {
            if (response.success) {
                // Заполняем список пользователей, которых можно добавить в группу
                const usersList = $('#users-list');
                usersList.empty();
                response.users.forEach(user => {
                    usersList.append(`
                        <li>
                            <input type="checkbox" name="user" value="${user.id}" /> ${user.username}
                        </li>
                    `);
                });
            } else {
                alert('Ошибка при загрузке списка пользователей');
            }
        }
    });
});

// Обработчик кнопки "Добавить" пользователей в группу
// Отправка запросов на присоединение к группе для выбранных пользователей
$('#add-users-button').click(function () {
    const groupId = $('#add-user-modal').data('group-id');

    // Собираем ID выбранных пользователей
    const selectedUserIds = [];
    $('#users-list input[name="user"]:checked').each(function () {
        selectedUserIds.push($(this).val());
    });

    if (selectedUserIds.length === 0) {
        alert('Выберите хотя бы одного пользователя!');
        return;
    }

    // Отправляем запрос для каждого выбранного пользователя
    selectedUserIds.forEach(userId => {
        $.ajax({
            url: '/send_group_join_request',
            method: 'POST',
            data: { group_id: groupId, user_id: userId },
            success: function (response) {
                if (!response.success) {
                    alert(`Ошибка при отправке запроса пользователю ${userId}: ${response.message}`);
                    console.log(`Error sending join request to user ${userId}: ${response.message}`);
                }
            },
            error: function () {
                alert(`Ошибка при отправке запроса пользователю ${userId}`);
            }
        });
    });

    alert('Запросы на присоединение отправлены!');
    $('#add-user-modal').modal('hide');
});
