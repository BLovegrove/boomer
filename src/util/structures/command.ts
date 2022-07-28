import { CommandInteraction } from "discord.js"
import { ExtendedClient } from "./extendedclient"

export type Command = {
    data: any,
    execute(interaction: CommandInteraction, client: ExtendedClient): Promise<undefined> | Promise<void>
}