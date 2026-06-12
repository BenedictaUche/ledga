import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-exception-inbox',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './exception-inbox.component.html',
  styleUrl: './exception-inbox.component.scss'
})
export class ExceptionInboxComponent {
  @Input() exceptions: any[] = [];
  @Input() operatorId: string = '';
  @Output() resolved = new EventEmitter<void>();

  resolving: Record<string, boolean> = {};

  constructor(private api: ApiService) {}

  async resolve(exceptionId: string, status: 'resolved' | 'dismissed') {
    this.resolving[exceptionId] = true;
    try {
      await this.api.resolveException(exceptionId, this.operatorId, status);
      this.resolved.emit();
    } finally {
      this.resolving[exceptionId] = false;
    }
  }

  severityClass(severity: string): string {
    return severity === 'high' ? 'high' : severity === 'medium' ? 'medium' : 'low';
  }

  typeLabel(type: string): string {
    const labels: Record<string, string> = {
      'low_stock': 'Low stock',
      'overdue_credit': 'Overdue credit',
      'large_credit': 'Large credit',
      'parse_failed': 'Parse failed',
      'unusual_sale': 'Unusual sale'
    };
    return labels[type] || type;
  }
}
