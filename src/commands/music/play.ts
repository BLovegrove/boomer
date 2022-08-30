import { SlashCommandBuilder } from "@discordjs/builders";
import { CommandInteraction } from "discord.js";
import { MusicHandler, VoiceHandler } from "../../util/handlers";
import { ExtendedClient, Command } from "../../util/structures";

export const command: Command = {
    data: new SlashCommandBuilder()
        .setName("play")
        .setDescription("Plays music! Summons boomer if he isn't running, adds a song to the queue if he is.")
        .addStringOption(option => option
            .setName('search')
            .setDescription('The name/artist/url of the song you want to find')
        )
        ,
    async execute(interaction: CommandInteraction, client: ExtendedClient) {
        const MH = new MusicHandler(client)

        const searchString = interaction.options.getString('search')

        if (searchString) {
            await MH.play(interaction, searchString)
            return
        }

        const VH = new VoiceHandler(client)
        const player = await VH.ensureVoice(interaction)

        if (!player) {
            return
        }

        if (!player.paused) {
            await interaction.reply({content: "Nothing is paused - try entering a YouTube or Soundcloud URL to play a new track instead.", ephemeral: true})
            return
        }

        player.pause(false)
        await interaction.reply("Track resumed :arrow_forward:")
        return
    }
}