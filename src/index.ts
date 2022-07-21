import { Intents } from "discord.js"
import { Manager } from "erela.js";
import config from "./config.json"
import { Boomer } from "./structures/boomer"

// create client with all normal + dm permissions + an erela manager
const client = new Boomer({
    intents: [
        Intents.FLAGS.GUILDS
    ]}, 
    new Manager({
    // The nodes to connect to, optional if using default lavalink options
    nodes: [{
        host: config.lavalink.host,
        password: config.lavalink.password,
        port: config.lavalink.port,
        identifier: config.lavalink.id
    }],
    // Method to send voice data to Discord
    send: (id, payload) => {
        const guild = client.guilds.cache.get(id);

        // NOTE: FOR ERIS YOU NEED JSON.stringify() THE PAYLOAD
        if (guild) guild.shard.send(payload);
    }
}))

client.manager.on("nodeConnect", node => {
    console.log(`Node '${node.options.identifier}' is online.`)
})

// add one-time listener for login alert
client.once("ready", () => { 
    
    if (client.user && client.manager)
    {
        console.log("Initialising lava manager...")
        client.manager.init(client.user.id);
        console.log(`${client.user.tag} is online.`)
    }
    else
    {
        console.log("Failed to init lava manager / discord client.");
    }
})

// monitor for slash commands and handle them seperately
client.on("interactionCreate", async interaction => {
    
    if (interaction.isCommand()) {
        const command = client.commands.get(interaction.commandName);

        if (!command) return;

        try {
            await command.execute(interaction, client);
        } catch (error) {
            console.error(error);
            await interaction.reply({ content: 'There was an error while executing this command!', ephemeral: true });
        }
    }
})

// THIS IS REQUIRED. Send raw events to Erela.js
client.on("raw", d => client.manager.updateVoiceState(d));

// log bot in to discord
client.connect()