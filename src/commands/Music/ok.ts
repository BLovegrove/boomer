import { SlashCommandBuilder } from "@discordjs/builders";
import { CommandInteraction } from "discord.js";
import { VoiceHelper } from "../../util/helpers";
import { ExtendedClient, Command } from "../../util/structures";
import config from "../../config.json"

export const command: Command = {
    data: new SlashCommandBuilder()
        .setName("ok")
        .setDescription("Summons boomer to your voice channel without playing anything.")
        .addSubcommand(command => 
            command
                .setName("boomer")
                .setDescription("Summons boomer to your voice channel without playing anything.")
        )
        ,
    async execute(interaction: CommandInteraction, client: ExtendedClient) {

        const VH = new VoiceHelper(client)

        await interaction.deferReply()
        const player = await VH.ensureVoice(interaction)
        if (!player) {
            return
        }

        await interaction.editReply(`Joined <#${player.voiceChannel}>`)
        player.setVolume(config.music.volumeDefault)
        client.manager.emit("queueEnd")
    }
}