import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { SupabaseService } from '../../services/supabase.service';
import { ExceptionInboxComponent } from '../../components/exception-inbox/exception-inbox.component';
import { ShopCardComponent } from '../../components/shop-card/shop-card.component';

const OPERATOR_ID = '00000000-0000-0000-0000-000000000001';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule, ExceptionInboxComponent, ShopCardComponent],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss'
})
export class DashboardComponent implements OnInit {
  operatorId = OPERATOR_ID;
  shops: any[] = [];
  shopSummaries: Record<string, any> = {};
  exceptions: any[] = [];
  loading = true;

  constructor(private supabase: SupabaseService) {}

  async ngOnInit() {
    await Promise.all([
      this.loadShops(),
      this.loadExceptions()
    ]);
    this.loading = false;
  }

  async loadShops() {
    this.shops = await this.supabase.getShops(this.operatorId);
    await Promise.all(
      this.shops.map(async shop => {
        const summary = await this.supabase.getTodaySummary(shop.id);
        this.shopSummaries[shop.id] = summary;
      })
    );
  }

  async loadExceptions() {
    this.exceptions = await this.supabase.getPendingExceptions(this.operatorId);
  }

  async onExceptionResolved() {
    await this.loadExceptions();
  }

  get totalProfitToday(): number {
    return Object.values(this.shopSummaries)
      .reduce((sum: number, s: any) => sum + (s?.total_profit || 0), 0);
  }

  get totalExceptions(): number {
    return this.exceptions.length;
  }

  get activeShops(): number {
    return Object.values(this.shopSummaries)
      .filter((s: any) => s?.status === 'open').length;
  }
}
