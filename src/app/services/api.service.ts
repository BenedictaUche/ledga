import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { firstValueFrom } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private base = environment.apiUrl;

  constructor(private http: HttpClient) {}

  async sendMessage(shopId: string, message: string) {
    return firstValueFrom(
      this.http.post<any>(`${this.base}/transactions/message`, {
        shop_id: shopId,
        message
      })
    );
  }

  async resolveException(exceptionId: string, operatorId: string, status: string) {
    return firstValueFrom(
      this.http.patch<any>(`${this.base}/exceptions/${exceptionId}/resolve`, {
        operator_id: operatorId,
        status
      })
    );
  }
}
