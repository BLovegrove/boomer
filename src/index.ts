import { Client, GatewayIntentBits, InteractionType } from "discord.js"
import config from "./config.json"
import { loadCommands, register } from "./helpers";
import path from "path"

// create client with all normal + dm permissions
const client = new Client({
    intents: [
        GatewayIntentBits.Guilds, 
        GatewayIntentBits.GuildMessages, 
        GatewayIntentBits.DirectMessages
    ]
})

// grab the command files and generate a collection from them
const commands = loadCommands(path.join(__dirname, "commands"))
// register the commands with the discord API to display them on the server
register(commands)

// add one-time listener for login alert
client.once("ready", () => {
    console.log(`${client.user?.tag} is online.`)
})

// monitor for slash commands and handle them seperately
client.on("interactionCreate", async interaction => {
    
    switch (interaction.type) {
        case InteractionType.ApplicationCommand:

            const command = commands.get(interaction.commandName);

            if (!command) return;

            try {
                await command.execute(interaction, client);
            } catch (error) {
                console.error(error);
                await interaction.reply({ content: 'There was an error while executing this command!', ephemeral: true });
            }

            break;
    
        default:
            break;
    }
})

// log bot in to discord
client.login(config.token)