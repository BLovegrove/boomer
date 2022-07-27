import { Intents } from "discord.js"
import { Manager, Player } from "erela.js";
import customFilter from "erela.js-filters";
import Spotify from "erela.js-spotify";
import config from "./config.json"
import { VoiceHelper } from "./util/helpers";
import { Boomer } from "./util/structures/boomer"

const nodes = [{
    host: config.lavalink.host,
    password: config.lavalink.password,
    port: config.lavalink.port
}];

// create client with all normal + dm permissions + an erela manager
const client = new Boomer({
    intents: [
        Intents.FLAGS.GUILDS,
        Intents.FLAGS.GUILD_MESSAGES,
        Intents.FLAGS.GUILD_VOICE_STATES
    ]},  
    new Manager({
    // The nodes to connect to, optional if using default lavalink options
    nodes,
    // Method to send voice data to Discord
    send: (id, payload) => {
        const guild = client.guilds.cache.get(id);
        if (guild) guild.shard.send(payload);
    },
    plugins: [
        // Load filter presets from erela.js-filters
        new customFilter(),
        new Spotify({
            clientID: config.spotify.clientID,
            clientSecret: config.spotify.secret
        })
    ]
}))

// Emitted whenever a node encountered an error
client.manager.on("nodeError", (node, error) => {
    console.log(`Node "${node.options.identifier}" encountered an error: ${error.message}.`)
})

client.manager.once("nodeConnect", node => {
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
            const interactionState = [
                (interaction.deferred ? "DEFERRED" : ""), 
                (interaction.replied ? "REPLIED" : "")
            ].filter(Boolean).join("_")
            
            switch(interactionState) {
                case "DEFERRED":
                    await interaction.editReply({ content: `${error}` });
                    break;
                case "DEFERRED_REPLIED":
                    await interaction.followUp({ content: `${error}`, ephemeral: true });
                    break;
                case "REPLIED":
                    await interaction.reply({ content: `${error}`, ephemeral: true });
                    break;
            }
            
            throw new Error("Command errored. Shuting down. This could be intentional, but check bot output just in case.")
        }
    }
})

client.manager.on("trackEnd", async node => {
    const player = VoiceHelper.fetchPlayer(client)
    if (player) {
        await VoiceHelper.updateStatus(client, player)
    }
})

// THIS IS REQUIRED. Send raw events to Erela.js
client.on("raw", d => client.manager.updateVoiceState(d));

// log bot in to discord
client.connect()