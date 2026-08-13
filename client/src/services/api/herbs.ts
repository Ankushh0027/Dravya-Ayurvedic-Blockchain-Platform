import api from './axios'
import { ApiResponse } from '@/types/api'
import { Herb } from '@/types/herb'

export const HerbService = {
  async getAllHerbs(): Promise<Herb[]> {
    const response = await api.get<ApiResponse<{ herbs: Herb[] }>>('/herbs')
    return response.data.data!.herbs || []
  }
}
