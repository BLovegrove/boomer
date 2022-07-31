import { CommandInteraction } from "discord.js"
import { ExtendedClient } from "./extended-client"

export type Command = {
    data: any,
    execute(interaction: CommandInteraction, client: ExtendedClient): Promise<undefined> | Promise<void>
}