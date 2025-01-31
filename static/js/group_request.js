// Обработчик клика по кнопке "+" для добавления пользователей в группу
$(document).on('click', '.add-user-btn', function() {
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
        success: function(response) {
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
$('#add-users-button').click(function() {
    const groupId = $('#add-user-modal').data('group-id');  // Получаем groupId
    const selectedUsers = [];
    
    // Получаем всех выбранных пользователей
    $('input[name="user"]:checked').each(function() {
        selectedUsers.push($(this).val());
    });
    console.log(selectedUsers);

    // Отправляем выбранных пользователей на сервер
    $.ajax({
        url: '/add_users_to_group',
        method: 'POST',
        data: {
            group_id: groupId,
            users: selectedUsers
        },
        success: function(response) {
            if (response.success) {
                alert('Пользователи успешно добавлены!');
                $('#add-user-modal').modal('hide');
            } else {
                alert(`Ошибка при добавлении пользователей:\n ${response.message}`);
            }
        }
    });
});
