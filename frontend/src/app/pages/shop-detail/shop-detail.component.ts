import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { SupabaseService } from '../../services/supabase.service';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-shop-detail',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
  templateUrl: './shop-detail.component.html',
  styleUrl: './shop-detail.component.scss'
})
export class ShopDetailComponent implements OnInit {
  shopId = '';
  shop: any = null;
  summary: any = null;
  transactions: any[] = [];
  creditLedger: any[] = [];
  loading = true;
  sending = false;
  message = '';
  sendResult: any = null;
  activeTab: 'transactions' | 'credit' = 'transactions';
  closingDay = false;
  dayClosedSummary: any = null;

  constructor(
    private route: ActivatedRoute,
    private supabase: SupabaseService,
    private api: ApiService
  ) {}

  async ngOnInit() {
    this.shopId = this.route.snapshot.paramMap.get('id') || '';
    await this.loadAll();
    this.loading = false;
  }

  async loadAll() {
    const [shops, summary, transactions, credit] = await Promise.all([
      this.supabase.getShops('00000000-0000-0000-0000-000000000001'),
      this.supabase.getTodaySummary(this.shopId),
      this.supabase.getShopTransactions(this.shopId),
      this.supabase.getCreditLedger(this.shopId)
    ]);
    this.shop = shops.find((s: any) => s.id === this.shopId);
    this.summary = summary;
    this.transactions = transactions || [];
    this.creditLedger = credit || [];
  }

  async sendMessage() {
    if (!this.message.trim() || this.sending) return;
    this.sending = true;
    this.sendResult = null;
    try {
      const result = await this.api.sendMessage(this.shopId, this.message);
      this.sendResult = result;
      this.message = '';
      await this.loadAll();
    } catch (e) {
      this.sendResult = { status: 'error', message: 'Failed to send message' };
    } finally {
      this.sending = false;
    }
  }

  async closeDay() {
    if (this.closingDay) return;
    this.closingDay = true;
    try {
      const result = await this.api.closeBusinessDay(this.shopId);
      this.dayClosedSummary = result.summary;
      await this.loadAll();
    } catch (e) {
      console.error('Failed to close day', e);
    } finally {
      this.closingDay = false;
    }
  }

  get profitMargin(): number {
    if (!this.summary?.total_sales) return 0;
    return Math.round((this.summary.total_profit / this.summary.total_sales) * 100);
  }
}
