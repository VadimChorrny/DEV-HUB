client.on('message', msg => {//Отвечает игроку

if(msg.content.startsWith("Выдать")) {
if(msg.member.permissions.has('MANAGE_ROLES')){
let role = msg.guild.roles.find(c => c.name === msg.content.split(" ")[1])
let user = msg.mentions.members.first();
user.addRole(role.id);
msg.reply(`Пользователю была выдана роль!` );
console.log(`Пользователю была выдана роль `)
} else {
msg.reply(`Вы не имеете право выдавать роли!`);
console.log(`Пользователь не имеет право выдавать роли!`);
}
}
});
