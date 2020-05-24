import { Component, OnInit } from '@angular/core';
import { HttpClient } from "@angular/common/http";
import { environment } from 'src/environments/environment';

@Component({
  selector: 'app-about',
  templateUrl: './about.component.html',
  styleUrls: ['./about.component.css']
})
export class AboutComponent implements OnInit {

  node_serve_url = '';
  date_stamp_str = ''
  navbarOpen = false

  constructor(private httpClient: HttpClient) { }

  toggleNavbar() { this.navbarOpen = !this.navbarOpen; }

  ngOnInit(): void {
    // Setup backend connection. Https connection if in production mode.
    if(environment.production){
      this.node_serve_url = "https://sonicboards.com:3000"
    }else{ this.node_serve_url = "http://localhost:3000" }

    this.httpClient
    .post(this.node_serve_url + '/api/config', {})
    .subscribe((data : string)=> { 
      var w = new Date(data)
      var d = w.getDate() < 10 ? '0' + w.getDate() : w.getDate()
      var m = w.getMonth() < 9 ? '0' + (w.getMonth()+1) : (w.getMonth()+1)
      this.date_stamp_str = `${m}-${d}-${w.getFullYear()}`
    })
  }

}
