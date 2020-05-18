import { Component } from '@angular/core';
import { Router, NavigationEnd } from '@angular/router'
import { filter } from 'rxjs/operators';

// ng add @ng-bootstrap/ng-bootstrap
// ng add angular-cli-ghpages

declare let gtag: Function;

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {

  constructor(public router: Router){   

  this.router.events.subscribe(event => {
    if(event instanceof NavigationEnd){
        gtag('config', 'G-T6BRRGPMF2', {'page_path': event.urlAfterRedirects});
      }
    }
  )

  }
  
}
