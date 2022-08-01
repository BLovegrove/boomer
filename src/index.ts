import { Intents } from "discord.js"
import { Manager } from "erela.js";
import filter from "erela.js-filters";
import Spotify from "erela.js-spotify";
import config from "./config.json"
import { EventHandler } from "./util/handlers";
import { ExtendedClient } from "./util/structures/extended-client"
import path from "path"

const nodes = [{
    host: config.lavalink.host,
    password: config.lavalink.password,
    port: config.lavalink.port
}];

// create client with all normal + dm permissions + an erela manager
const client = new ExtendedClient({
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
        new filter(),
        new Spotify({
            clientID: config.spotify.clientID,
            clientSecret: config.spotify.secret
        })
    ]
}))

EventHandler.load(client, path.join(__dirname, "./events"))

// log bot in to discord
client.connect()