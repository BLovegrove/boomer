import { Boomer } from "../structures"
import { CommandInteraction, GuildMember } from "discord.js"
import { Player } from "erela.js"

import config from "../../config.json"

export class VoiceHelper {

    client: Boomer

    constructor(client: Boomer) {
        this.client = client
    }

    /**
     * multi purpose catch-all meant to go before a command. 
     * checks that the interaction is within a guild and inside
     * a voice channel. fetches existing player if there is 
     * one else creates a new one using details from given interaction.
     * @param interaction Discord.js CommandInteraction
     * @returns erela.js player
     */
    async ensureVoice(interaction: CommandInteraction)
    {

        // sender validation: in guild
        if (!(interaction.member instanceof GuildMember)) {
            interaction.reply({ content: "Try sending this from within a server.", ephemeral: true });
            return null
        }
        
        // sender validation: in voice
        if (!interaction.member.voice.channel) {
            interaction.reply({ content: "you need to join a voice channel.", ephemeral: true });
            return null
        }

        // this fetches the player if one exists. otherwise gerenates a new one
        const player = this.client.manager.create({
            guild: interaction.guild!.id,
            voiceChannel: interaction.member.voice.channel!.id,
            textChannel: interaction.channel!.id,
        });

        // defer reply. makes bot say 'thinking...' for up to 15 minutes 
        // vs. stock 3 seconds
        interaction.deferReply({ephemeral: true})

        if (player.state == "DISCONNECTED") {
            // set up some default states and connect the player to requesters VC
            player.set("pages", 0)
            player.connect()
            return null
        } else {
            // ensure player is connected to the same VC as the member interacting with it
            if (player.voiceChannel !== interaction.member.voice.channel!.id) {
                await interaction.editReply(`You need to be in <#${player.voiceChannel}> to do that.`)
                return null
            }

            // success! this should be the output at all times :)))
            return player
        }
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
        await this.updateStatus(player)
        return null
    }

    /**
     * Updates the activity and status to match what boomer is doing.
     * playing music: online & shows 'listening to (song). idle: shows 
     * nothing and idle status.
     * @param player erela.js player
     */
    async updateStatus(player: Player) {

        var suffix = ""

        // attached modidifiers present to the activity message
        if (player.trackRepeat) {
            suffix = " (on repeat)"
        } else {
            suffix = ""
        }

        // this shouldnt ever happen but it makes typescript shut up about
        // 'things possibly being null' :(
        if (!this.client.user) {
            console.log("Catastrophic error. no user attached to bot. Leaving status unchanged");
            return null
        }

        if (player.queue.current) {
            // update status based on current song

            this.client.user.setActivity(
                player.queue.current.title + suffix,
                {
                    type: 'LISTENING'
                }
            )
            this.client.user.setStatus("online")
        } else {
            // update status to idle and show listening to 'nothing'

            this.client.user.setActivity(
                "nothing.",
                {
                    type: "LISTENING"
                }
            )
            this.client.user.setStatus("idle")
        }

        console.log(`Updated activity info to: ${this.client.user.presence.activities}`);
        console.log(`Updated status info to: ${this.client.user.presence.status}`)
        return null
    }
}