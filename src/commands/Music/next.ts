import { SlashCommandBuilder } from "@discordjs/builders";
import { CommandInteraction } from "discord.js";
import { VoiceHelper } from "../../util/helpers";
import { Boomer, Command } from "../../util/structures";

export const command: Command = {
    data: new SlashCommandBuilder()
        .setName("next")
        .setDescription("Skip to the next item in queue. Temporary replacement for /skip (coming soon)")
        ,
    async execute(interaction: CommandInteraction, client: Boomer) {
        const VH = new VoiceHelper(client)
        const player = await VH.ensureVoice(interaction)
        if (!player) {
            return
        }

        player.stop(1)

        return interaction.reply("Skipping to next song!")
    }
}