// TypeScript interfaces for StickyStoryBlocks component

export interface CardItem {
  type: 'card'
  id: string
  content: string
}

export interface HeadingItem {
  type: 'heading'
  id: string
  text: string
}

export type StoryItem = CardItem | HeadingItem

export interface StoryBlockGroup {
  type: 'sticky-model-group' | 'full-width-sticky-model'
  modelPath: string
  items: StoryItem[]
  groupId?: string
}

export interface CameraPosition {
  x: number
  y: number
  z: number
}

export interface CameraConfig {
  position: CameraPosition
  fov: number
  near: number
  far: number
}

export interface ViewerOptions {
  camera: CameraConfig
  fitCamera: boolean
}

export interface ModelDimensions {
  width: number
  height: number
}

export interface CardActivationEvent {
  cardId: string
  cardIndex: number
  groupIndex: number
  modelPath: string
}
