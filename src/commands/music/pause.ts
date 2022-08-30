import { SlashCommandBuilder } from "@discordjs/builders";
import { CommandInteraction } from "discord.js";
import { VoiceHandler } from "../../util/handlers";
import { ExtendedClient, Command } from "../../util/structures";

export const command: Command = {
    data: new SlashCommandBuilder()
        .setName("pause")
        .setDescription("Stops the music, to be resumed later")
        ,
    async execute(interaction: CommandInteraction, client: ExtendedClient) {
        const VH = new VoiceHandler(client)
        const player = await VH.ensureVoice(interaction)
        if (!player) {
            return
        }

        if (player.paused) {
            await interaction.reply({content: "Already paused.", ephemeral: true})
            return
        }

        player.pause(true)
        await interaction.reply("Track paused :pause_button:")
        return
    }
}