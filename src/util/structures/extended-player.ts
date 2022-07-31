import { Player } from "erela.js"

export interface ExtendedPlayer extends Player {
    
    nightcore: boolean
    vaporwave: boolean
    bassboost: boolean
    pop: boolean
    soft: boolean
    treblebass: boolean
    eightdimension: boolean
    karaoke: boolean
    vibrato: boolean
    tremolo: boolean
    reset(): Function
}