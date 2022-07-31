import { ExtendedClient } from "./extended-client"

export type ClientEvent = {
    name: string,
    listen(client: ExtendedClient): Promise<undefined> | Promise<void>
}