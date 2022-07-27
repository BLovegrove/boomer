import { Player, Track } from "erela.js";
import { Boomer } from "../structures";
import { VoiceHelper } from "./voice";
import config from "../../config.json"
import { CommandInteraction } from "discord.js";
import { ClearedEmbedBuilder } from "../structures";

export class QueueHelper {

    private client: Boomer
    private VH: VoiceHelper

    constructor(client: Boomer) {
        this.client = client
        this.VH = new VoiceHelper(client)
    }

    updatePages(player: Player) {
        player.set('pages', Math.ceil(player.queue.length / config.music.listPageLength))
    }

    async clear(interaction: CommandInteraction, index?: number) {
        const player = await this.VH.ensureVoice(interaction)
        if (!player) {
            return
        }

        if (!index) {
            player.queue.clear()
            player.set('pages', 0)
            interaction.reply(":boom: Queue cleared!")

        } else {
            const cleared = player.queue.remove(index).at(0)
            interaction.reply({embeds: [
                new ClearedEmbedBuilder(interaction, cleared, player).toJSON()
            ]})
        }
    }
}