export interface StorageRequest {
  id: number
  presigned_data: PresignedData
}

export interface PresignedData {
  url: string
  fields: []
}

export interface StorageFile {
  id: number
}
