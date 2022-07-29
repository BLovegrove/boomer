import { Player } from "erela.js"
import customFilter from "erela.js-filters"

export interface ExtendedPlayer extends Player {
    nightcore: boolean
    reset: Function
}