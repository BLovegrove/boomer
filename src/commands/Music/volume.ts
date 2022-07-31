import { SlashCommandBuilder } from "@discordjs/builders";
import { CommandInteraction, GuildMember, PermissionResolvable } from "discord.js";
import { VoiceHandler } from "../../util/handlers";
import { ExtendedClient, Command } from "../../util/structures";
import config from "../../config.json"

const clamp = (num: number, min: number, max: number) => Math.min(Math.max(num, min), max);

export const command: Command = {
    data: new SlashCommandBuilder()
        .setName("volume")
        .setDescription("Checks / changes the voilume level.")
        .addNumberOption(option =>
            option
                .setName("level")
                .setDescription("The volume level you want to set the bot to.")
        )
        ,
    async execute(interaction: CommandInteraction, client: ExtendedClient) {
        const sender = interaction.member as GuildMember
        const VH = new VoiceHandler(client)
        const player = await VH.ensureVoice(interaction)
        if (!player) {
            return
        }

        var volumeLevel = interaction.options.getNumber('level')
        var volumeIndicator = ""

        if (volumeLevel) {
            if (!sender.permissions.has(config.dev.permissionFlag as PermissionResolvable)) {
                volumeLevel = clamp(volumeLevel, 0, 100)
                player.setVolume(Math.ceil(volumeLevel / 2))
            } else {
                volumeLevel = Math.max(0, volumeLevel)
                player.setVolume(Math.ceil(volumeLevel / 2))
            }

        } else {
            volumeLevel = clamp(player.volume * 2, 0, 100)
        }
        
        if (volumeLevel <= 33) {
            volumeIndicator = ":speaker:"

        } else if (volumeLevel > 33 && volumeLevel <= 66) {
            volumeIndicator = ":sound:"

        } else {
            volumeIndicator = ":loud_sound:"
        }

        await interaction.reply(`${volumeIndicator} Volume is set to ${volumeLevel}%`)
    }
}