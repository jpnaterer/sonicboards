import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-about',
  templateUrl: './about.component.html',
  styleUrls: ['./about.component.css']
})
export class AboutComponent implements OnInit {

  date_stamp_str = ''
  navbarOpen = false

  constructor() { }

  toggleNavbar() { this.navbarOpen = !this.navbarOpen; }

  ngOnInit(): void {
    var today = new Date()
    var w = new Date(today.setDate(today.getDate()-today.getDay()-1))
    var d = w.getDate() < 10 ? '0' + w.getDate() : w.getDate()
    var m = w.getMonth() < 9 ? '0' + (w.getMonth()+1) : (w.getMonth()+1)
    this.date_stamp_str = `${m}-${d}-${w.getFullYear()}`
  }

}
