import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-shop-card',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './shop-card.component.html',
  styleUrl: './shop-card.component.scss'
})
export class ShopCardComponent {
  @Input() shop: any;
  @Input() summary: any;

  get statusLabel(): string {
    if (!this.summary) return 'No activity';
    return this.summary.status.charAt(0).toUpperCase() + this.summary.status.slice(1);
  }

  get statusClass(): string {
    if (!this.summary) return 'inactive';
    return this.summary.status;
  }
}
