import { SlashCommandBuilder } from "@discordjs/builders";
import { CommandInteraction } from "discord.js";
import { VoiceHandler } from "../../util/handlers";
import { ExtendedClient, Command, ProgressEmbedBuilder } from "../../util/structures";

export const command: Command = {
    data: new SlashCommandBuilder()
        .setName("now")
        .setDescription("Shows info about the current song! Playtime, title, thumbnail, link, etc.")
        ,
    async execute(interaction: CommandInteraction, client: ExtendedClient) {
        const VH = new VoiceHandler(client)
        const player = await VH.ensureVoice(interaction)
        if (!player) {
            return
        }

        const embed = new ProgressEmbedBuilder(interaction, player).toJSON()
        await interaction.reply({embeds: [embed]})
    }
}