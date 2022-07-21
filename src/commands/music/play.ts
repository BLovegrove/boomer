import { GuildMember } from "discord.js";
import { SlashCommandBuilder } from "@discordjs/builders"
import { Command, Boomer } from "../../structures"

// export var must always be 'command' - see 'add command module files to collection' in index.ts
// : Command type adds strong typing for interaction and client args! Thank god for typescript

export const command: Command = {
    data: new SlashCommandBuilder()
        .setName("play")
        .setDescription("play a song")
        .addStringOption(option =>
            option
                .setName("url")
                .setDescription("Song url from Youtube, Spotify, etc.")
                .setRequired(true)
        ),
    async execute(interaction, client) {

        if (!(interaction.member instanceof GuildMember)) {
            return interaction.reply("Try sending this from within a server.")
        }
        if (!interaction.member.voice.channel) {
            return interaction.reply("you need to join a voice channel.");
        }

        console.log(interaction.options.);
        
        // const {commandName, options} = interaction

        // const searchUrl: any = options.get('url', true).value
        
        // await client.manager.search(searchUrl, interaction.member);

        //     try {
        //         // Search for tracks using a query or url, using a query searches youtube automatically and the track requester object
        //         res = 
        //         // Check the load type as this command is not that advanced for basics
        //         if (res.loadType === "LOAD_FAILED") throw res.exception;
        //         else if (res.loadType === "PLAYLIST_LOADED") throw { message: "Playlists are not supported with this command." };
        //     } catch (err) {
        //         return message.reply(`there was an error while searching: ${err.message}`);
        //     }

        //     if (res.loadType === "NO_MATCHES") return message.reply("there was no tracks found with that query.");

        //     // Create the player 
        //     const player = client.manager.create({
        //         guild: message.guild.id,
        //         voiceChannel: message.member.voice.channel.id,
        //         textChannel: message.channel.id,
        //     });

        //     // Connect to the voice channel and add the track to the queue
        //     player.connect();
        //     player.queue.add(res.tracks[0]);

        //     // Checks if the client should play the track if it's the first one added
        //     if (!player.playing && !player.paused && !player.queue.size) player.play()

        //     return message.reply(`enqueuing ${res.tracks[0].title}.`);
        // }
        return interaction.reply("Hi :)")
    }
}