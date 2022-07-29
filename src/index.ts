import { Channel, ChannelManager, Intents, Interaction, TextChannel, VoiceChannel } from "discord.js"
import { Manager, Player, Track } from "erela.js";
import filter from "erela.js-filters";
import Spotify from "erela.js-spotify";
import config from "./config.json"
import { QueueHelper, VoiceHelper } from "./util/helpers";
import { ExtendedClient } from "./util/structures/extendedclient"

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

                case "REPLIED":
                    await interaction.editReply({ content: `${error}`});
                    break;

                case "DEFERRED_REPLIED":
                    await interaction.followUp({ content: `${error}`, ephemeral: true });
                    break;
                
                default:
                    await interaction.reply({ content: `${error}`, ephemeral: true });
                    break;
            }
            
            throw new Error("Command errored. Shuting down. This could be intentional, but check bot output just in case.")
        }
    }
})

client.on("voiceStateUpdate", async (before, after) => {
    const player = VoiceHelper.fetchPlayer(client)
    if (!player) {
        return
    }

    if (!before.channel ||
        after.channel || 
        after.channelId == player.voiceChannel || 
        before.channelId != player.voiceChannel
        ) {
        return
    }

    const channel = client.channels.cache.get(player.voiceChannel as string) as VoiceChannel
    if (!channel) {
        return
    }

    if (channel.members.size == 1) {
        const VH = new VoiceHelper(client)
        VH.disconnect(player)
    }
})

client.manager.on("trackStart", async node => {
    const player = VoiceHelper.fetchPlayer(client)
    if (player) {
        await VoiceHelper.updateStatus(client, player)
    }
})

client.manager.on("queueEnd", async node => {
    const player = VoiceHelper.fetchPlayer(client)
    const VH = new VoiceHelper(client)
    if (!player) {
        return
    }

    player.setVolume(config.music.volumeIdle)

    const results = await player.search(config.music.idleTrack)

    if (!results || !results.tracks || results.loadType != "TRACK_LOADED") {
        player.queue.clear()
        VH.disconnect(player)

        if (!player.textChannel) {
            console.log("Couldnt find a text channel when queuing idle track.")
            return
        }

        const channel = client.channels.cache.get(player.textChannel) as TextChannel
        channel.send(":warning: Nothing found when looking for idle music! look for a new video.")
    }

    player.set('idle', true)
    player.setTrackRepeat(true)

    const track = results.tracks.at(0) as Track
    player.queue.add(track, 0)

    if (!player.playing) {
        await player.play()
    }
})

// THIS IS REQUIRED. Send raw events to Erela.js
client.on("raw", d => client.manager.updateVoiceState(d));

// log bot in to discord
client.connect()