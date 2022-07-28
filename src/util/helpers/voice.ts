import { ExtendedClient } from "../structures"
import { CommandInteraction, GuildMember } from "discord.js"
import { Player } from "erela.js"

import config from "../../config.json"

/**
 * Helps manage the voice state with common guards and convenient connection/disconnection methods 
 */
export class VoiceHelper {

    client: ExtendedClient

    /**
     * Note: Any command using ensureVoice is deferred to account for lavalink response times.
     * use editReply for any ineraction reply after ensureVoice runs.
     * @param client modified discord.js client called 'Boomer'.
     */
    constructor(client: ExtendedClient) {
        this.client = client
    }

    /**
     * make sure you never run this in a scenario where a player doesnt exist.
     * inbuilt guard for that coming soon.
     * @param client Custom discord.js client Boomer
     * @returns erela.js player
     */
    static fetchPlayer(client: ExtendedClient) {
        return client.manager.get(config.bot.guildID) as Player
    }

    /**
     * multi purpose catch-all meant to go before a command. 
     * checks that the interaction is within a guild and inside
     * a voice channel. fetches existing player if there is 
     * one else creates a new one using details from given interaction.
     * @param interaction Discord.js CommandInteraction
     * @returns erela.js player
     */
    async ensureVoice(interaction: CommandInteraction) {

        // sender validation: in guild
        if (!(interaction.member instanceof GuildMember) || !interaction.guild || !interaction.channel) {
            interaction.reply({ content: "Try sending this from within a server.", ephemeral: true });
            return
        }

        // sender validation: in voice
        if (!interaction.member.voice.channel) {
            interaction.reply({ content: "You need to join a voice channel.", ephemeral: true });
            return
        }

        // this fetches the player if one exists. otherwise gerenates a new one
        const player = this.client.manager.create({
            guild: interaction.guild.id,
            voiceChannel: interaction.member.voice.channel.id,
            textChannel: interaction.channel.id,
        });

        if (player.state == "DISCONNECTED") {
            // set up some default states and connect the player to requesters VC
            player.set("pages", 0)
            player.set("idle", false)
            player.connect()
            
        } else if (player.voiceChannel !== interaction.member.voice.channel.id) {
            // ensure player is connected to the same VC as the member interacting with it
            await interaction.reply({ content: `Already in <#${player.voiceChannel}> :rolling_eyes:`, ephemeral: true})
            await interaction.followUp({content: `${config.bot.name} can't be in two places at once. Join the linked channel to use ${config.bot.pronoun}.`, ephemeral: true})

        }

        // success! this should be the output at all times :)))
        return player
    }

    /**
     * Resets the state of the player back to its defaults.
     * @param player erela.js player
     */
    async disconnect(player: Player) {
        player.queue.clear()
        player.stop()
        player.setTrackRepeat(false)
        player.setQueueRepeat(false)
        player.setVolume(config.music.volumeDefault)
        player.disconnect()
        player.destroy()
        await VoiceHelper.updateStatus(this.client, player)
        return
    }

    /**
     * Updates the activity and status to match what boomer is doing.
     * playing music: online & shows 'listening to (song). idle: shows 
     * nothing and idle status.
     * @param player erela.js player
     */
    static async updateStatus(client: ExtendedClient, player: Player) {

        var suffix = ""

        // attached modidifiers present to the activity message
        if (player.trackRepeat) {
            suffix = " (on repeat)"
        }

        if (player.playing) {
            // update status based on current song

            client.user!.setActivity(
                player.queue.current!.title + suffix,
                {
                    type: 'LISTENING'
                }
            )
            client.user!.setStatus("online")
            
        } else {
            // update status to idle and show listening to 'nothing'

            client.user!.setActivity(
                "nothing.",
                {
                    type: "LISTENING"
                }
            )
            client.user!.setStatus("idle")
        }

        console.log(`Updated activity info to: ${client.user!.presence.activities}`);
        console.log(`Updated status info to: ${client.user!.presence.status}`)
        return
    }
}