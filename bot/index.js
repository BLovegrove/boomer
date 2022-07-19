// discord js core content
const { Client, Intents, Collection } = require('discord.js')
// rest API content
const { REST } = require('@discordjs/rest')
const { Routes } = require('discord-api-types/v9')
// IO modules
const path = require('node:path')
const fs = require('node:fs')
// custom config
const config = require('./config.json')

const client = new Client({ intents: [Intents.FLAGS.GUILDS] });

// load commands 
const commands = new Collection()
const commandPath = path.join(__dirname, "commands");
fs.readdirSync(commandPath).forEach(dir => {
    const files = fs.readdirSync(`${commandPath}/${dir}/`).filter(file => file.endsWith('.js'))

    for (const file of files) {
        const command = require(`${commandPath}/${dir}/${file}`);
        commands.set(command.data.name, command);
    }
})

// register global commands
const rest = new REST({ version: '9' }).setToken(config.token);
(async () => {
    try {
        console.log('Started refreshing application (/) commands.');

        const commandInfo = []
        commands.forEach(command => {
            commandInfo.push(command.data.toJSON())
        })

        await rest.put(Routes.applicationCommands(config.clientID), { body: commandInfo });

        console.log('Successfully reloaded application (/) commands.');
    } catch (error) {
        console.error(error);
    }
})();

// log bot in to discord
client.login(config.token)

// declare bot online
client.on('ready', () => {
    console.log(`${client.user.tag} is online!`);
});

// listen for commands
client.on('interactionCreate', async interaction => {
    if (!interaction.isCommand()) return;

    const command = commands.get(interaction.commandName);

    if (!command) return;

    try {
        await command.execute(interaction);
    } catch (error) {
        console.error(error);
        await interaction.reply({ content: 'There was an error while executing this command!', ephemeral: true });
    }
});