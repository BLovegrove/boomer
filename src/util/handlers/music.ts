// # ----------------------------------Imports --------------------------------- #
import { ExtendedClient, SkipEmbedBuilder } from "../structures"
import config from "../../config.json"
import { Player, SearchResult, Track, TrackUtils, UnresolvedTrack } from "erela.js";
import { CommandInteraction } from "discord.js";
import { VoiceHandler } from "./voice";
import { QueueHandler } from "./queue";
import { PlaylistEmbedBuilder, TrackEmbedBuilder } from "../structures";

// # ----------------------------------Config ---------------------------------- #

export class MusicHandler {

    private client: ExtendedClient;
    private VH: VoiceHandler
    QH: QueueHandler

    constructor(client: ExtendedClient) {
        this.client = client;
        this.VH = new VoiceHandler(client)
        this.QH = new QueueHandler(client)
    }

    private async addTrack (
        interaction: CommandInteraction, 
        player: Player, 
        track: Track | undefined=undefined, 
        tracks: Track[] | undefined=undefined, 
        result: SearchResult | undefined=undefined) {

        var embed = {}

        if (track) {
            embed = new TrackEmbedBuilder(interaction, track, player).toJSON()

            player.queue.add(track)
            console.log("Track added to queue");

        } else if (tracks && result) {
            embed = new PlaylistEmbedBuilder(interaction, result, player).toJSON()

            tracks.forEach(track => {
                player.queue.add(track)
            })
            console.log("Playlist added to queue");
        } 

        if (player.get<boolean>("idle")) {
            player.set("idle", false)
            player.setTrackRepeat(false)
            player.setVolume(config.music.volumeDefault)
            player.stop(1)
            
        } else if (!player.playing) {
            player.setVolume(config.music.volumeDefault)
            await player.play()
        } 
        
        interaction.editReply({embeds: [embed]})
    }

    async play(interaction: CommandInteraction, query: string) {
        const player = await this.VH.ensureVoice(interaction)
        if (!player){
            return

        } else {
            console.log(`Attempting to play song... Query: ${query}`)
        }
        
        await interaction.deferReply()

        const result = await player.search(query)
        console.log(result)

        try {

            switch (result.loadType) {
                case "LOAD_FAILED":
                    interaction.editReply("Failed to load track, please use a URL or different search term");
                    break;

                case "NO_MATCHES":
                    interaction.editReply("404 Song not found! Try something else.");
                    break;

                case "SEARCH_RESULT":
                    var track = result.tracks.at(0)
                    this.addTrack(interaction, player, track)
                    break;

                case "TRACK_LOADED":
                    var track = result.tracks.at(0)
                    this.addTrack(interaction, player, track)
                    break;

                case "PLAYLIST_LOADED":
                    var tracks = result.tracks;
                    this.addTrack(interaction, player, undefined, tracks, result)
                    break;

                default:
                    await interaction.editReply("Something unexpected happen. Contact your server owner immediately and let them know the exact command you tried to run.");
                    console.log(`Load type for play request defaulted. query '${query}' result as follows:`);
                    console.log(result);
                    break;
            }

        } catch (e) {
            console.log("Failed to play track. Error:" + e)
            return
        }

        this.QH.updatePages(player)

        return
    }
    async skip(interaction: CommandInteraction, index: number, trim_queue = true ) {
        if (!this.client.playerExists){
            await interaction.reply(":warning: There is no player running. Play a song first.")
            return
        }

        const player = await this.VH.ensureVoice(interaction)
        if (!player){
            return
        }

        if (player.queue.length == 0 && !player.trackRepeat) {
            await interaction.reply(":notepad_spiral: End of queue - time for your daily dose of idle tunes.")
            player.stop()
            return
        }

        if (player.trackRepeat) {
            const nextTrack = player.queue.current

            if (!nextTrack) {
                await interaction.reply(config.error.trackNotFound)
                return
            }

            const embed = new SkipEmbedBuilder(interaction, nextTrack, player, 0).toJSON()
            await interaction.reply({content: ":repeat_one: Repeat enabled - looping song.", embeds:[embed] }) 
            player.seek(0)
            console.log("Skipped (Repeating song).");
            return
        }
        
        if (index < 0) {
            await interaction.reply({content: ":warning: That index is too low! Queue starts at #1.",ephemeral: true})
            console.log(`Skip failed. Index too low(Expected: >=1. Recieved: ${index})`)
            return

        } else if (index > player.queue.length) {
            await interaction.reply({content: `:warning: That index is too high! Queue only ${player.queue.length} items long.`,ephemeral: true})
            console.log(`Skip failed. Index too low(Expected: <=${player.queue.length}. Recieved: ${index})`)
            return
        
        } else {

            if (trim_queue) {
                console.log(`Skipped queue to track ${index} of ${player.queue.length}`)

                if (index - 1 != 0) {
                    player.queue.remove(0, index - 1)
                }
            
            } else {
                console.log(`Jumped to track ${index} of ${player.queue.length} in queue.`)
                const jumpTrack = player.queue.remove(index - 1).at(0)

                if (!jumpTrack) {
                    await interaction.reply(config.error.trackNotFound)
                    return
                }

                player.queue.add(jumpTrack, 0) 
            }

            // resolve the track if it hasnt been done already
            var nextTrack = player.queue.at(0)
            if (TrackUtils.isUnresolvedTrack(nextTrack)) {
                nextTrack = await TrackUtils.getClosestTrack(nextTrack as UnresolvedTrack)
            }

            if (!nextTrack) {
                await interaction.reply(config.error.trackNotFound)
                return
            }

            player.stop()
            console.log("Skipped current track")

            const embed = new SkipEmbedBuilder(interaction, nextTrack, player, index).toJSON()
            await interaction.reply({embeds: [embed]}) 
            
            this.QH.updatePages(player) 
            await VoiceHandler.updateStatus(this.client, player)

            return
        }
    }
}