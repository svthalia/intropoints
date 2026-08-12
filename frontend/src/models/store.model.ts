export interface Store {
  id: number
  name: string
  description: string
  tournament: number
  tournament_slug: string
}

export interface StoreItem {
  id: number
  name: string
  description: string
  price: number
  thumbnail: string | null
}

export interface Purchase {
  team: number
  item: number
}

export interface UsableItem {
  id: number
  item: StoreItem
}

export interface Inventory {
  id: number
  items: UsableItem[]
}
